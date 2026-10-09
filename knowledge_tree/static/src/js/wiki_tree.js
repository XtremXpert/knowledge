import { Component, proxy, t, untrack, useEffect, useProps } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";

const STORAGE_KEY = "knowledge_tree";

function loadPrefs() {
    try {
        const prefs = JSON.parse(browser.localStorage.getItem(STORAGE_KEY) || "{}");
        return { expanded: prefs.expanded || [], hidden: Boolean(prefs.hidden) };
    } catch {
        return { expanded: [], hidden: false };
    }
}

/** Lowercase, without accents: "Été" matches "ete". */
function normalize(text) {
    return (text || "")
        .normalize("NFD")
        .replace(/[̀-ͯ]/g, "")
        .toLowerCase();
}

/**
 * Wiki tree shown beside the page form, Notion/AFFiNE style: categories and
 * pages, filter, "+" to add a page in a category, drag and drop to move.
 */
export class WikiTree extends Component {
    static template = "knowledge_tree.WikiTree";
    props = useProps({
        ...standardWidgetProps,
        record: t.object(),
    });

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.ui = useService("ui");
        const prefs = loadPrefs();
        this.state = proxy({
            nodes: [],
            loaded: false,
            filter: "",
            expanded: prefs.expanded,
            hidden: prefs.hidden,
            dropId: null,
        });
        this.dragId = null;
        useEffect(() => {
            // Reload when another page is displayed.
            const resId = this.props.record.resId;
            untrack(() => this.load(resId));
        });
    }

    get currentId() {
        return this.props.record.resId;
    }

    async load(resId) {
        this.state.nodes = await this.orm.call("document.page", "maison_tree_nodes", []);
        this.state.loaded = true;
        this.expandAncestors(resId);
    }

    savePrefs() {
        try {
            browser.localStorage.setItem(
                STORAGE_KEY,
                JSON.stringify({ expanded: this.state.expanded, hidden: this.state.hidden })
            );
        } catch {
            // Private browsing or blocked storage: the tree still works.
        }
    }

    get byId() {
        return new Map(this.state.nodes.map((node) => [node.id, node]));
    }

    expandAncestors(resId) {
        const byId = this.byId;
        let node = byId.get(resId);
        let changed = false;
        while (node && node.parent_id) {
            if (!this.state.expanded.includes(node.parent_id)) {
                this.state.expanded.push(node.parent_id);
                changed = true;
            }
            node = byId.get(node.parent_id);
        }
        if (changed) {
            this.savePrefs();
        }
    }

    /** Tree of {id, name, isCategory, children}, filtered when searching. */
    get roots() {
        const filter = normalize(this.state.filter.trim());
        const currentName = this.props.record.data.name;
        const nodes = this.state.nodes.map((node) => ({
            ...node,
            // The current page's title follows the form while typing.
            name: node.id === this.currentId && currentName ? currentName : node.name,
            isCategory: node.type === "category",
            children: [],
        }));
        const byId = new Map(nodes.map((node) => [node.id, node]));
        const roots = [];
        const orphans = [];
        for (const node of nodes) {
            const parent = byId.get(node.parent_id);
            if (parent) {
                parent.children.push(node);
            } else if (node.isCategory) {
                roots.push(node);
            } else {
                orphans.push(node);
            }
        }
        const sort = (list) => {
            list.sort(
                (a, b) => b.isCategory - a.isCategory || a.name.localeCompare(b.name)
            );
            list.forEach((node) => sort(node.children));
        };
        sort(roots);
        sort(orphans);
        if (orphans.length) {
            roots.push({
                id: "none",
                name: _t("Without category"),
                isCategory: true,
                isVirtual: true,
                children: orphans,
            });
        }
        if (!filter) {
            return roots;
        }
        // Keep matches and their ancestors; matched categories keep everything.
        const keep = (list) =>
            list
                .map((node) => {
                    if (normalize(node.name).includes(filter)) {
                        return { ...node, forceOpen: true };
                    }
                    const children = keep(node.children);
                    return children.length ? { ...node, children, forceOpen: true } : null;
                })
                .filter(Boolean);
        return keep(roots);
    }

    /** Visible rows, depth first: the template renders a flat list. */
    get rows() {
        const rows = [];
        const visit = (nodes, depth) => {
            for (const node of nodes) {
                rows.push({ node, depth });
                if (node.isCategory && this.isOpen(node)) {
                    visit(node.children, depth + 1);
                }
            }
        };
        visit(this.roots, 0);
        return rows;
    }

    isOpen(node) {
        return node.forceOpen || node.isVirtual || this.state.expanded.includes(node.id);
    }

    toggle(node) {
        if (node.isVirtual) {
            return;
        }
        const index = this.state.expanded.indexOf(node.id);
        if (index >= 0) {
            this.state.expanded.splice(index, 1);
        } else {
            this.state.expanded.push(node.id);
        }
        this.savePrefs();
    }

    toggleHidden() {
        this.state.hidden = !this.state.hidden;
        this.savePrefs();
    }

    onFilterInput(ev) {
        this.state.filter = ev.target.value;
    }

    async onClick(node) {
        if (node.isCategory) {
            this.toggle(node);
            return;
        }
        if (node.id === this.currentId) {
            return;
        }
        // Like the form pager: save pending changes, then show the page
        // (as a one-page pager: the tree replaces the list navigation).
        const model = this.props.record.model;
        if ((await model.root.isDirty()) && !(await model.root.save())) {
            return;
        }
        await model.load({ resId: node.id, resIds: [node.id] });
        this.env.config.setDisplayName?.(this.props.record.model.root.data.name);
    }

    newPage(category) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "document.page",
            views: [[false, "form"]],
            target: "current",
            context: {
                default_type: "content",
                default_parent_id: category.isVirtual ? false : category.id,
            },
        });
    }

    onDragStart(ev, node) {
        if (node.isVirtual) {
            ev.preventDefault();
            return;
        }
        this.dragId = node.id;
        ev.dataTransfer.effectAllowed = "move";
        ev.dataTransfer.setData("text/plain", String(node.id));
    }

    canDrop(node) {
        return node.isCategory && !node.isVirtual && this.dragId && this.dragId !== node.id;
    }

    onDragOver(ev, node) {
        if (this.canDrop(node)) {
            ev.preventDefault();
            ev.dataTransfer.dropEffect = "move";
            this.state.dropId = node.id;
        }
    }

    onDragLeave(node) {
        if (this.state.dropId === node.id) {
            this.state.dropId = null;
        }
    }

    onDragEnd() {
        this.dragId = null;
        this.state.dropId = null;
    }

    async onDrop(ev, node) {
        ev.preventDefault();
        const dragId = this.dragId;
        this.onDragEnd();
        if (!dragId || !node.isCategory || node.isVirtual || dragId === node.id) {
            return;
        }
        if (dragId === this.currentId) {
            // The current page: go through the form, which keeps unsaved edits.
            const record = this.props.record.model.root;
            await record.update({ parent_id: { id: node.id, display_name: node.name } });
            await record.save();
        } else {
            try {
                await this.orm.call("document.page", "maison_tree_move", [[dragId], node.id]);
            } finally {
                await this.load(this.currentId);
            }
        }
        if (!this.state.expanded.includes(node.id)) {
            this.state.expanded.push(node.id);
            this.savePrefs();
        }
        await this.load(this.currentId);
    }
}

export const wikiTree = {
    component: WikiTree,
};

registry.category("view_widgets").add("maison_wiki_tree", wikiTree);

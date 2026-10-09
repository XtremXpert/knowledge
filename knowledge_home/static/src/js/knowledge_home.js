import { Component, markup, onMounted, proxy, useProps } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";
import { deserializeDateTime, formatDate } from "@web/core/l10n/dates";
import { registry } from "@web/core/registry";
import { debounce } from "@web/core/utils/timing";
import { useService } from "@web/core/utils/hooks";
import { standardActionServiceProps } from "@web/webclient/actions/action_plugin";

const TREE_KEY = "knowledge_home_tree";

function loadExpanded() {
    try {
        const raw = browser.localStorage.getItem(TREE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch {
        return [];
    }
}

function saveExpanded(expanded) {
    try {
        browser.localStorage.setItem(TREE_KEY, JSON.stringify(expanded));
    } catch {
        // Private browsing: the tree still works, the open folders are just
        // not remembered.
    }
}

/** Opens a wiki page in its form view, like the search menu does. */
export function openPage(action, id) {
    return action.doAction({
        type: "ir.actions.act_window",
        res_model: "document.page",
        res_id: id,
        views: [[false, "form"]],
        target: "current",
    });
}

function toResult(page) {
    return {
        ...page,
        name: markup(page.name),
        snippet: markup(page.snippet),
        date: page.write_date ? formatDate(deserializeDateTime(page.write_date)) : "",
    };
}

/**
 * Landing page of the Knowledge app: category and page tree on the left,
 * real categories and recent pages in the centre, search on top. Everything
 * is loaded through search(), so the Odoo record rules decide what each user
 * may see.
 */
export class KnowledgeHome extends Component {
    static template = "knowledge_home.Home";
    props = useProps({ ...standardActionServiceProps });

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.ui = useService("ui");
        this.state = proxy({
            nodes: [],
            recent: [],
            expanded: loadExpanded(),
            loading: true,
            query: "",
            results: [],
            searched: false,
            treeOpen: false,
        });
        this.requestId = 0;
        this.runSearch = debounce(this._search.bind(this), 250);
        onMounted(() => this.load());
    }

    async load() {
        const data = await this.orm.call("document.page", "maison_home_data", []);
        this.state.nodes = data.nodes;
        this.state.recent = data.recent;
        this.state.loading = false;
    }

    get tree() {
        const nodes = this.state.nodes.map((node) => ({ ...node, children: [] }));
        const byId = new Map(nodes.map((node) => [node.id, node]));
        const roots = [];
        for (const node of nodes) {
            const parent = byId.get(node.parent_id);
            if (parent) {
                parent.children.push(node);
            } else {
                roots.push(node);
            }
        }
        const sort = (list) => {
            list.sort(
                (a, b) =>
                    b.is_category - a.is_category || a.name.localeCompare(b.name)
            );
            list.forEach((node) => sort(node.children));
        };
        sort(roots);
        return roots;
    }

    get rows() {
        const rows = [];
        const visit = (nodes, depth) => {
            for (const node of nodes) {
                rows.push({ node, depth });
                if (node.is_category && this.isOpen(node)) {
                    visit(node.children, depth + 1);
                }
            }
        };
        visit(this.tree, 0);
        return rows;
    }

    isOpen(node) {
        return node.is_category && this.state.expanded.includes(node.id);
    }

    toggle(node) {
        const index = this.state.expanded.indexOf(node.id);
        if (index >= 0) {
            this.state.expanded.splice(index, 1);
        } else {
            this.state.expanded.push(node.id);
        }
        saveExpanded(this.state.expanded);
    }

    toggleTree() {
        this.state.treeOpen = !this.state.treeOpen;
    }

    onNodeClick(node) {
        if (node.is_category && node.children.length) {
            this.toggle(node);
        } else {
            this.openNode(node);
        }
    }

    openNode(node) {
        openPage(this.action, node.id);
        if (this.ui.isSmall) {
            // Close the drawer once a page is opened on a small screen.
            this.state.treeOpen = false;
        }
    }

    onSearchInput(ev) {
        this.state.query = ev.target.value;
        this.runSearch();
    }

    async _search() {
        const query = this.state.query.trim();
        const requestId = ++this.requestId;
        if (query.length < 2) {
            this.state.results = [];
            this.state.searched = false;
            return;
        }
        const pages = await this.orm.call("document.page", "maison_search", [query]);
        if (requestId !== this.requestId) {
            return;
        }
        this.state.results = pages.map(toResult);
        this.state.searched = true;
    }

    open(page) {
        openPage(this.action, page.id);
    }
}

registry.category("actions").add("knowledge_home.home", KnowledgeHome);

import {Plugin} from "@html_editor/plugin";
import {isContentEditable, isTextNode} from "@html_editor/utils/dom_info";
import {_t} from "@web/core/l10n/translation";
import {debounce} from "@web/core/utils/timing";
import {proxy} from "@odoo/owl";
import {PageLinkList} from "./page_link_list";

const MAX_TERM_LENGTH = 80;

/**
 * Links between wiki pages, AFFiNE style: typing "[[" or "@" (or the
 * "/page" command) opens a page search; picking a page inserts a link to
 * it, and an unknown title can be created on the spot.
 */
export class PageLinkPlugin extends Plugin {
    static id = "maisonPageLink";
    static dependencies = ["history", "overlay", "dom", "selection", "delete"];
    /** @type {import("plugins").EditorResources} */
    resources = {
        on_input_handlers: this.onInput.bind(this),
        on_deleted_handlers: () => this.refresh(),
        user_commands: [
            {
                id: "maisonPageLink",
                title: _t("Link to a page"),
                description: _t("Search a wiki page and link to it"),
                icon: "description",
                run: this.startFromCommand.bind(this),
            },
        ],
        powerbox_items: [
            {
                categoryId: "navigation",
                commandId: "maisonPageLink",
                keywords: [_t("page"), _t("wiki"), _t("mention")],
            },
        ],
    };

    setup() {
        this.listOverlay = this.dependencies.overlay.createOverlay(PageLinkList, {
            className: "popover",
        });
        this.listState = proxy({list: []});
        // Active trigger ("[[" or "@") while a page search is open.
        this.trigger = null;
        this.requestId = 0;
        this.addDomListener(this.document, "keydown", (ev) => {
            if (ev.key === "Escape") {
                this.stop();
            }
        });
        // A click on a page link opens the page (AFFiNE style) rather than
        // the editor's link popover.
        this.addDomListener(
            this.editable,
            "click",
            (ev) => {
                const link = ev.target.closest?.("a.o_mk_page_link");
                const id = parseInt(
                    link?.getAttribute("href")?.match(/document_pages\/(\d+)/)?.[1]
                );
                if (!id || ev.ctrlKey || ev.metaKey || ev.shiftKey) {
                    return;
                }
                ev.preventDefault();
                ev.stopPropagation();
                this.services.action.doAction({
                    type: "ir.actions.act_window",
                    res_model: "document.page",
                    res_id: id,
                    views: [[false, "form"]],
                    target: "current",
                });
            },
            true
        );
    }

    /**
     * @param {InputEvent} ev
     */
    onInput(ev) {
        const selection = this.dependencies.selection.getEditableSelection();
        if (
            !isTextNode(selection.startContainer) ||
            !isContentEditable(selection.startContainer) ||
            !selection.isCollapsed
        ) {
            this.stop();
            return;
        }
        const text = selection.startContainer.textContent;
        const offset = selection.startOffset;
        if (ev.data === "[" && text[offset - 2] === "[") {
            this.trigger = "[[";
        } else if (ev.data === "@" && (offset < 2 || /\s/.test(text[offset - 2]))) {
            // "@" only after a space, so e-mail addresses stay untouched.
            this.trigger = "@";
        }
        this.refresh();
    }

    startFromCommand() {
        this.dependencies.dom.insert("[[");
        this.trigger = "[[";
        this.refresh();
    }

    stop() {
        this.trigger = null;
        this.listOverlay.close();
    }

    /**
     * Locates the trigger and the search term before the caret. Looked up
     * again on each keystroke: the editor may split or replace text nodes
     * (e.g. on spaces).
     */
    locate() {
        if (!this.trigger) {
            return null;
        }
        const selection = this.dependencies.selection.getEditableSelection();
        if (!selection.isCollapsed) {
            return null;
        }
        // After an insertion, the caret may sit in the parent element,
        // right after the text node.
        let node = selection.startContainer;
        let caret = selection.startOffset;
        if (!isTextNode(node)) {
            node = node.childNodes[caret - 1];
            caret = node?.textContent.length;
        }
        if (!node || !isTextNode(node)) {
            return null;
        }
        // The trigger may sit in a preceding sibling text node.
        let startNode = node;
        let before = node.textContent.slice(0, caret);
        let start = before.lastIndexOf(this.trigger);
        let sibling = node.previousSibling;
        while (start < 0 && sibling && isTextNode(sibling)) {
            before = sibling.textContent + before;
            start = sibling.textContent.lastIndexOf(this.trigger);
            startNode = sibling;
            sibling = sibling.previousSibling;
        }
        if (start < 0) {
            return null;
        }
        // "before" starts with startNode's text, so "start" indexes both.
        const term = before
            .slice(start + this.trigger.length)
            .replace(/[\u00a0\s]/g, " ");
        if (term.length > MAX_TERM_LENGTH || term.includes("]") || / {2}$/.test(term)) {
            return null;
        }
        return {startNode, start, node, end: caret, term};
    }

    refresh() {
        if (!this.trigger) {
            return;
        }
        if (!this.locate()) {
            this.stop();
            return;
        }
        this.search();
    }

    search = debounce(this._search, 150);
    async _search() {
        const found = this.locate();
        if (!found) {
            this.stop();
            return;
        }
        const term = found.term;
        const requestId = ++this.requestId;
        const recordInfo = this.config.getRecordInfo?.() || {};
        const pages = await this.services.orm.call(
            "document.page",
            "maison_link_search",
            [term.trim()],
            {exclude_id: recordInfo.resId || false}
        );
        if (requestId !== this.requestId || !this.locate()) {
            return;
        }
        const list = pages.map((page) => ({
            value: `page-${page.id}`,
            id: page.id,
            label: page.name,
            description: page.category,
            icon: "description",
        }));
        const title = term.trim();
        const exists = pages.some(
            (page) => page.name.toLowerCase() === title.toLowerCase()
        );
        // A new page goes in the current page's category: none chosen yet,
        // no creation (the page would then fail the category check).
        if (title && !exists && this.getCategoryId()) {
            list.push({
                value: "create",
                label: _t("Create “%s”", title),
                title,
                icon: "add",
                isCreate: true,
            });
        }
        if (!list.length) {
            this.listOverlay.close();
            return;
        }
        this.listState.list = list;
        this.listOverlay.open({
            props: {
                state: this.listState,
                onSelect: (item) => this.select(item),
                overlay: this.listOverlay,
            },
        });
    }

    getCategoryId() {
        const category = this.config.getRecordInfo?.().data?.parent_id;
        return category?.id || (Array.isArray(category) ? category[0] : false);
    }

    async select(item) {
        const found = this.locate();
        this.stop();
        if (!found) {
            return;
        }
        let page = {id: item.id, name: item.label};
        if (item.isCreate) {
            page = await this.services.orm.call("document.page", "maison_link_create", [
                item.title,
                this.getCategoryId(),
            ]);
        }
        this.dependencies.selection.setSelection({
            anchorNode: found.startNode,
            anchorOffset: found.start,
            focusNode: found.node,
            focusOffset: found.end,
        });
        this.dependencies.delete.deleteSelection();
        const link = this.document.createElement("a");
        link.href = `/odoo/document_pages/${page.id}`;
        link.className = "o_mk_page_link";
        link.textContent = page.name;
        const fragment = this.document.createDocumentFragment();
        fragment.append(link, this.document.createTextNode(" "));
        this.dependencies.dom.insert(fragment);
        this.dependencies.history.commit();
    }
}

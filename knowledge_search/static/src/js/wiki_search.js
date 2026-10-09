import { Component, markup, onMounted, proxy, signal, useProps } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardActionServiceProps } from "@web/webclient/actions/action_plugin";
import { debounce } from "@web/core/utils/timing";
import { deserializeDateTime, formatDate } from "@web/core/l10n/dates";

/** Opens a wiki page in its form view. */
export function openPage(action, id) {
    return action.doAction({
        type: "ir.actions.act_window",
        res_model: "document.page",
        res_id: id,
        views: [[false, "form"]],
        target: "current",
    });
}

export function toResult(page) {
    return {
        ...page,
        name: markup(page.name),
        snippet: markup(page.snippet),
        date: page.write_date
            ? formatDate(deserializeDateTime(page.write_date))
            : "",
    };
}

/** "Search" menu of the wiki: one box, results with highlighted excerpts. */
export class WikiSearch extends Component {
    static template = "knowledge_search.WikiSearch";
    props = useProps({ ...standardActionServiceProps });

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.inputRef = signal.ref();
        this.state = proxy({ query: "", results: [], searched: false, loading: false });
        this.requestId = 0;
        this.search = debounce(this._search.bind(this), 250);
        onMounted(() => this.inputRef()?.focus());
    }

    onInput(ev) {
        this.state.query = ev.target.value;
        this.search();
    }

    onKeydown(ev) {
        if (ev.key === "Enter" && this.state.results.length) {
            this.open(this.state.results[0]);
        }
    }

    async _search() {
        const query = this.state.query.trim();
        const requestId = ++this.requestId;
        if (query.length < 2) {
            this.state.results = [];
            this.state.searched = false;
            return;
        }
        this.state.loading = true;
        const pages = await this.orm.call("document.page", "maison_search", [query]);
        if (requestId !== this.requestId) {
            return;
        }
        this.state.results = pages.map(toResult);
        this.state.searched = true;
        this.state.loading = false;
    }

    open(result) {
        openPage(this.action, result.id);
    }
}

registry.category("actions").add("knowledge_search.wiki_search", WikiSearch);

/** Ctrl+K, then "?": search the wiki from anywhere. */
registry.category("command_setup").add("?", {
    debounceDelay: 250,
    emptyMessage: _t("No page found"),
    name: _t("wiki pages"),
    placeholder: _t("Search the wiki..."),
});

registry.category("command_provider").add("maison_wiki_pages", {
    namespace: "?",
    async provide(options) {
        const orm = useService("orm");
        const action = useService("action");
        const query = (options.searchValue || "").trim();
        if (query.length < 2) {
            return [];
        }
        const pages = await orm.call("document.page", "maison_search", [query, 8]);
        return pages.map((page) => ({
            name: page.category ? `${page.title} — ${page.category}` : page.title,
            action: () => openPage(action, page.id),
        }));
    },
});

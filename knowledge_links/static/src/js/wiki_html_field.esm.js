import {HtmlField, htmlField} from "@html_editor/fields/html_field";
import {registry} from "@web/core/registry";
import {PageLinkPlugin} from "./page_link_plugin";

/** Html field of wiki pages: adds links to other pages ("[[", "@", "/page"). */
export class WikiHtmlField extends HtmlField {
    getConfig() {
        const config = super.getConfig();
        config.Plugins = [...config.Plugins, PageLinkPlugin];
        return config;
    }
}

registry.category("fields").add("maison_wiki_html", {
    ...htmlField,
    component: WikiHtmlField,
    additionalClasses: [...(htmlField.additionalClasses || []), "o_field_html"],
});

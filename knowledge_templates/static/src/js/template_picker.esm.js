import {Component, onWillStart, proxy, useProps} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

/** Cards to start a new page from a template (or blank). */
export class TemplatePicker extends Component {
    static template = "knowledge_templates.TemplatePicker";
    props = useProps({...standardFieldProps});

    setup() {
        this.orm = useService("orm");
        this.state = proxy({templates: []});
        onWillStart(async () => {
            this.state.templates = await this.orm.searchRead(
                "knowledge.page.template",
                [],
                ["name", "icon", "description"]
            );
        });
    }

    get selectedId() {
        return this.props.record.data[this.props.name]?.id || false;
    }

    async pick(template) {
        if (template) {
            await this.props.record.update({
                [this.props.name]: {id: template.id, display_name: template.name},
            });
        } else {
            await this.props.record.update({[this.props.name]: false, content: ""});
        }
    }
}

registry.category("fields").add("knowledge_template_picker", {
    component: TemplatePicker,
    supportedTypes: ["many2one"],
});

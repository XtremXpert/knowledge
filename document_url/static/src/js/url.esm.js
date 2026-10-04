/* Copyright 2014 Tecnativa - Pedro M. Baeza
 * Copyright 2021 Tecnativa - Víctor Martínez
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

// Odoo 20 : le Chatter vit dans @mail/chatter/web_portal_project et sa boîte
// de pièces jointes affiche nativement les pièces jointes de type « url »
// (bouton « Open Link ») ; il ne reste qu'à ajouter le bouton « Add URL » et
// à ouvrir le lien au clic au lieu de proposer un téléchargement.
import {AttachmentList} from "@mail/core/common/attachment_list";
import {Chatter} from "@mail/chatter/web_portal_project/chatter";
import {browser} from "@web/core/browser/browser";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

patch(Chatter.prototype, {
    setup() {
        super.setup(...arguments);
        this.action = useService("action");
    },

    get canAddUrl() {
        // Comme les boutons natifs : actif sur un enregistrement non sauvegardé
        // (onClickAddUrl l'enregistre d'abord).
        const thread = this.state.thread;
        return Boolean(thread && (thread.canPostMessage || !thread.id));
    },

    async onClickAddUrl() {
        const open = (thread) =>
            this.action.doAction("document_url.action_ir_attachment_add_url", {
                additionalContext: {
                    active_id: thread.id,
                    active_ids: [thread.id],
                    active_model: thread.model,
                },
                onClose: async () => {
                    await this.load(thread, ["attachments"]);
                    if (this.attachments.length) {
                        this.state.activePanel = this.CHATTER_PANEL.ATTACHMENT;
                    }
                    if (this.hasParentReloadOnAttachmentsChanged) {
                        this.reloadParentView();
                    }
                },
            });
        if (this.state.thread.id) {
            return open(this.state.thread);
        }
        // Enregistrement pas encore sauvegardé : même mécanisme que scheduleActivity.
        this.onThreadCreated = open;
        await this.webChatterProps.saveRecord?.();
    },
});

patch(AttachmentList.prototype, {
    canDownload(attachment) {
        return attachment.type !== "url" && super.canDownload(attachment);
    },

    onClickAttachment(attachment) {
        // Les liens YouTube gardent la visionneuse native ; les autres liens
        // s'ouvrent dans un nouvel onglet.
        if (
            !this.props.isSelecting &&
            attachment.type === "url" &&
            attachment.url &&
            !attachment.isViewable
        ) {
            browser.open(attachment.url, "_blank", "noopener");
            return;
        }
        return super.onClickAttachment(attachment);
    },
});

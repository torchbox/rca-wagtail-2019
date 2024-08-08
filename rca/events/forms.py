from rca.utils.forms import RCAPageAdminForm


class EventAdminForm(RCAPageAdminForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contact_model_title"].label = "Title"
        self.fields["contact_model_email"].label = "Email"
        self.fields["contact_model_url"].label = "URL"
        self.fields["contact_model_form"].label = "Form"
        self.fields["contact_model_image"].label = "Image"
        self.fields["contact_model_text"].label = "Text"
        self.fields["contact_model_link_text"].label = "Link text"

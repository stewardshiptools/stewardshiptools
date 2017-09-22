from django.views.generic.base import ContextMixin


class CSVResponseMixin(object):
    csv_filename = 'csvfile.csv'

    def get_csv_filename(self):
        return self.csv_filename

    def render_to_csv(self, data):
        response = HttpResponse(content_type='text/csv')
        cd = 'attachment; filename="{0}"'.format(self.get_csv_filename())
        response['Content-Disposition'] = cd

        writer = csv.writer(response)
        for row in data:
            writer.writerow(row)

        return response


class FileResponseMixin(object):
    """
    Mix in that lets you return a file attachment response.
    Requires you to define a filename.
    At the moment will only return an xml file.
    Add other file types (ie content_types) response methods as needed.
    """
    filename = None

    def get_filename(self):
        if self.filename is None:
            raise AssertionError("FileResponseMixin requires \"filename\" to be defined.")

        return self.filename

    def xml_file_response(self, data):
        response = HttpResponse(data, content_type='text/xml')
        cd = 'attachment; filename="{0}"'.format(self.get_filename())
        response['Content-Disposition'] = cd
        return response


class NavContextMixin(ContextMixin):
    '''
    Sets a context variable that is picked up by some JS in the base
    template that sets the open nav collapsible.

    Make sure you use reverse_lazy if you put this in the class definition.
    eg.
        sidenav_url = reverse_lazy('heritage:secureasset-dashboard')

    BEWARE!!!!!:
        - if you forget to user reverse_lazy the urlconf will break for the whole site.
    '''

    def get_context_data(self, **kwargs):
        context = super(NavContextMixin, self).get_context_data(**kwargs)
        try:
            context['nav_url'] = self.nav_url
        except AttributeError:
            print("Failed to get nav url class property for view.")
            pass
        return context


class EditObjectMixin(ContextMixin):
    """
    EditObjectMixin - adds context vars that control cancel, submit, and delete buttons
    Implementation:
        - CreateView: you probably only need to add ONE class property: edit_object_cancel_url.
            - use reverse_lazy or get awesome circular imports.
        - UpdateView:
            - add delete perm
            - override cancel_url method
            - override delet_url method

            EG:
                edit_object_delete_perm = 'crm.delete_organization'

                def get_edit_object_cancel_url(self):
                    return reverse_lazy('crm:organization-detail', args=[self.object.id])

                def get_edit_object_delete_url(self):
                    return reverse_lazy('crm:organization-delete', args=[self.object.id])

    """
    edit_object_delete_url = None
    edit_object_delete_perm = None
    edit_object_submit_selector = 'form'
    edit_object_submit_action_text = None
    edit_object_cancel_url = None

    def get_edit_object_delete_url(self):
        return self.edit_object_delete_url

    def get_edit_object_delete_perm(self):
        return self.edit_object_delete_perm

    def get_edit_object_submit_selector(self):
        return self.edit_object_submit_selector

    def get_edit_object_submit_action_text(self):
        return self.edit_object_submit_action_text

    def get_edit_object_cancel_url(self):
        return self.edit_object_cancel_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'edit_object_delete_url': self.get_edit_object_delete_url(),
            'edit_object_delete_perm': self.get_edit_object_delete_perm(),
            'edit_object_submit_selector': self.get_edit_object_submit_selector(),
            'edit_object_submit_action_text': self.get_edit_object_submit_action_text(),
            'edit_object_cancel_url': self.get_edit_object_cancel_url(),
        })
        return context

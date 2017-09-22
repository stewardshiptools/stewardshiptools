from django.db import models
from django.template.defaultfilters import slugify


class HelpText(models.Model):
    title = models.CharField(max_length=50, blank=False, null=False)
    html = models.TextField(blank=True, null=True)
    note = models.TextField(verbose_name="Note on this help text.", blank=True, null=True)

    @property
    def sanitized_html(self):
        # TODO implement help html sanitizing -- eg BeautifulSoup, remove <scripts>
        return self.html

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "help doc"
        ordering = ['title']


class PageHelp(models.Model):
    page_name = models.CharField(max_length=50, unique=True, blank=False, null=False)
    tooltip = models.CharField(max_length=50, default='Help')
    help_text = models.ManyToManyField(HelpText, blank=True)

    # Note: the slug will change (and therefore the url) if the title is updated.
    # Note: Don't think I'm going to use the slugs in urls quite yet.
    # slug = models.SlugField(blank=True)  # Blank is ok, null is not.
    # Note: use the save method below to auto-populate the slug field.

    def __str__(self):
        return self.page_name

        # def save(self, *args, **kwargs):
        #     self.slug = slugify(self.title)
        #     super(PageHelp, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Help doc assignment"

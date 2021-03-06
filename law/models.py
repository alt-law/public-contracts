import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.text import slugify


class Type(models.Model):
    name = models.CharField(max_length=254)
    dr_series = models.CharField(max_length=10)

    def get_absolute_url(self):
        name = "%s" % slugify(self.name)
        return reverse('law_type', args=[self.pk, name])

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'dr_series')


class Document(models.Model):
    type = models.ForeignKey(Type)
    number = models.CharField(max_length=20, null=True)

    creator_name = models.TextField()

    date = models.DateField()

    # summary of the publication.
    # Some documents don't have summary.
    summary = models.TextField(null=True)
    # text of the publication, in HTML.
    # Some documents don't have the text available.
    text = models.TextField(null=True)

    # Where it can be found in the internet (DRE)
    dre_doc_id = models.IntegerField(unique=True, db_index=True)
    dre_pdf_id = models.IntegerField(unique=True, db_index=True)

    # Where it can be found in the official book (DR)
    dr_series = models.CharField(max_length=10, db_index=True)
    dr_number = models.CharField(max_length=10)
    dr_supplement = models.CharField(max_length=50, null=True)
    dr_pages = models.CharField(max_length=50)

    # documents it refers to.
    references = models.ManyToManyField('self', symmetrical=False)

    def get_pdf_url(self):
        return "https://dre.pt/application/file/a/%d" % self.dre_pdf_id

    def get_absolute_url(self):
        name = "%s" % slugify(self.type.name)
        if self.number:
            name += '-%s' % self.number
        else:
            name += '-de-' + self.date.strftime('%d/%m/%Y')
        return reverse('law_view', args=[self.dre_doc_id, name])

    def get_minimal_url(self):
        return reverse('law_view', args=[self.dre_doc_id])

    def compose_summary(self):
        return self.summary

    def name(self):
        name = self.type.name

        if self.number:
            name = name + ' ' + self.number
        return name

    def update_references(self):
        from . import composer
        documents = composer.get_references(self).values_list('id', flat=True)
        self.references.add(*list(documents))

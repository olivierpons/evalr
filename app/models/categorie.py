from django.utils.translation import gettext_lazy as _
from django.db import models

from .regle import Regle
from .bulle import GroupeBulles


class CategoriesGroup(models.Model):
    links = models.ManyToManyField('Category', blank=True,
                                   through='CategoriesGroupCategory',
                                   symmetrical=False,
                                   related_name='group_categories')
    groupe_bulles = models.ForeignKey(GroupeBulles, blank=True,
                                      default=None, null=True,
                                      on_delete=models.CASCADE)
    description = models.CharField(max_length=150)
    exemple = models.CharField(max_length=150, blank=True, default=None,
                               null=True)

    def __str__(self):
        return _('{}{}').format(
            self.description,
            ' ({})'.format(self.exemple) if self.exemple else ''
        )

    class Meta:
        verbose_name = _("Group of categories")
        verbose_name_plural = _("Groups of categories")
        ordering = ['description']


class GroupeCategoriesRegles(models.Model):
    categoriesgroup_1 = models.ForeignKey(
        CategoriesGroup, related_name='gc1',
        help_text=_("Groups of categories of the current expression"),
        on_delete=models.CASCADE)
    categoriesgroup_2 = models.ForeignKey(
        CategoriesGroup, related_name='gc2',
        help_text=_("Groups of categories of the next expression"),
        on_delete=models.CASCADE)
    regles = models.ManyToManyField(Regle, blank=True,
                                    related_name='groupecategoriesregle_regle',
                                    through='GroupeCategoriesReglesRegle')

    def __str__(self):
        cs_g_1 = self.categoriesgroup_1
        cs_g_2 = self.categoriesgroup_2
        return _('{} + {} = ({} <> {}) -> {}').format(
            str(cs_g_1.description) if cs_g_1 else '?',
            str(cs_g_2.description) if cs_g_2 else '?',
            str(cs_g_1.exemple) if cs_g_1 else '?',
            str(cs_g_2.exemple) if cs_g_2 else '?',
            '-'.join([str(r) for r in self.regles.all()])
        )

    class Meta:
        verbose_name = _("Categories: groups of categories / rule")
        verbose_name_plural = _("Categories: groups of categories / rules")
        ordering = ['groupecategoriesreglesregle__importance']


class GroupeCategoriesReglesRegle(models.Model):
    groupecategoriesregles = models.ForeignKey('GroupeCategoriesRegles',
                                               on_delete=models.CASCADE)
    regle = models.ForeignKey(Regle, on_delete=models.CASCADE)
    importance = models.IntegerField(blank=False, default=1)

    def __str__(self):
        if self.groupecategoriesregles:
            gcr = self.groupecategoriesregles
            g1 = gcr.categoriesgroup_1.exemple \
                if gcr.categoriesgroup_1 is not None else '?'
            g2 = gcr.categoriesgroup_2.exemple \
                if gcr.categoriesgroup_2 is not None else '?'
        else:
            g1 = g2 = '??'
        if self.regle:
            regle = str(self.regle)
        else:
            regle = '??'
        return _(f'({g1} <> {g2}) -> {regle}')


class Category(models.Model):
    links = models.ManyToManyField('self', blank=True,
                                   through='CategoryLink',
                                   symmetrical=False,
                                   related_name='parent')
    groupe_bulles = models.ForeignKey(GroupeBulles, blank=True,
                                      default=None, null=True,
                                      on_delete=models.CASCADE)
    description = models.CharField(max_length=150)
    exemple = models.CharField(max_length=150, blank=True, default=None,
                               null=True)
    reference = models.CharField(max_length=200, blank=True, default=None,
                                 null=True)

    def __str__(self):
        return _('{}{}').format(self.description,
                                ' ({})'.format(self.exemple)
                                if self.exemple else '')

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class CategoriesGroupCategory(models.Model):
    group_categories = models.ForeignKey(CategoriesGroup,
                                         related_name='group',
                                         verbose_name=_("Group"),
                                         on_delete=models.CASCADE)
    category = models.ForeignKey(Category,
                                 related_name='category',
                                 verbose_name=_("Category"),
                                 on_delete=models.CASCADE)

    def __str__(self):
        # Only displayed in admin, and only when we edit 'group_categories'
        # for convenience, only display only the opposite = category
        return _('{}').format(self.category)


class CategoryLink(models.Model):
    src = models.ForeignKey(Category,
                            related_name='category_src',
                            verbose_name=_("Src link"),
                            on_delete=models.CASCADE)
    dst = models.ForeignKey(Category,
                            related_name='category_dst',
                            verbose_name=_("Dst link"),
                            on_delete=models.CASCADE)

    def __str__(self):
        return _('{} / {}').format(self.src, self.dst)


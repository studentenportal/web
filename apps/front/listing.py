"""Standardized search, filter and sort behavior for list views.

All lists on the portal follow the same query parameter conventions:

    q       case-insensitive full-text search
    sort    sort option (one of sort_options, first key is the default)
    <param> declared filters (value must be one of the filter choices)
    page    page number

The mixin works on top of Django's ListView (override get_base_queryset)
and can be used on any other view through apply_listing()/apply_search().
"""

from django.db.models import Q


class ListingMixin:
    """Adds standardized search, filter and sort handling to a list view.

    Subclasses may set:
        search_fields: tuple of field lookups searched via ?q=
        sort_options: ordered dict value -> {"label": str, "order_by": list}
        filter_options: dict param -> field lookup, e.g. {"dtype": "dtype"}
        filter_choices: dict param -> iterable of (value, label) pairs.
            If provided for a param, unknown values are ignored.
        search_placeholder: placeholder text for the search input
        paginate_by: page size (used by ListView)
    """

    search_fields = ()
    search_param = "q"
    sort_param = "sort"
    sort_options = {}
    filter_options = {}
    filter_choices = {}
    search_placeholder = "Suchen..."
    paginate_by = 50

    # --- search ---

    def get_search_query(self):
        return (self.request.GET.get(self.search_param, "") or "").strip()

    def apply_search(self, queryset):
        query = self.get_search_query()
        if query and self.search_fields:
            search_q = Q()
            for field in self.search_fields:
                search_q |= Q(**{"%s__icontains" % field: query})
            queryset = queryset.filter(search_q)
        return queryset

    # --- filters ---

    def get_filter_choices(self):
        return self.filter_choices

    def filter_value(self, param):
        value = self.request.GET.get(param, "") or None
        if value is None:
            return None
        choices = self.get_filter_choices().get(param)
        if choices is not None and value not in {str(v) for v, _ in choices}:
            return None
        return value

    def apply_filters(self, queryset):
        for param, field in self.filter_options.items():
            value = self.filter_value(param)
            if value is not None:
                queryset = queryset.filter(**{field: value})
        return queryset

    # --- sort ---

    def get_current_sort(self):
        sort = self.request.GET.get(self.sort_param, "") or None
        if sort not in self.sort_options:
            sort = next(iter(self.sort_options), None)
        return sort

    def apply_sort(self, queryset):
        sort = self.get_current_sort()
        if sort is not None:
            queryset = queryset.order_by(*self.sort_options[sort]["order_by"])
        return queryset

    # --- combined ---

    def apply_listing(self, queryset):
        """Apply search, filters and sorting to a queryset."""
        return self.apply_sort(self.apply_filters(self.apply_search(queryset)))

    def get_base_queryset(self):
        """The unfiltered queryset (overridden by subclasses)."""
        return super().get_queryset()

    def get_queryset(self):
        return self.apply_listing(self.get_base_queryset())

    # --- context ---

    def listing_context(self):
        filters = []
        for param in self.filter_options:
            choices = self.get_filter_choices().get(param, [])
            filters.append(
                {
                    "param": param,
                    "value": self.filter_value(param) or "",
                    "choices": [(str(value), label) for value, label in choices],
                }
            )
        current_sort = self.get_current_sort()
        return {
            "search_query": self.get_search_query(),
            "search_placeholder": self.search_placeholder,
            "current_sort": current_sort,
            "sort_options": [
                {
                    "value": value,
                    "label": options["label"],
                    "active": value == current_sort,
                }
                for value, options in self.sort_options.items()
            ],
            "filter_options": filters,
            "list_action": self.request.path,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.listing_context())
        return context

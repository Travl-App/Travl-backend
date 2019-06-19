class Paginator:
    def __init__(self, current_page, model=None, items=None, query=None, items_per_page=10):
        self.current_page = current_page
        self.items_per_page = items_per_page
        self.query = query
        self.item_list = items
        self.model = model

    @property
    def count(self):
        if self.query:
            return self.query.count()
        elif self.item_list:
            return len(self.item_list)
        elif self.model:
            return self.model.objects.count()
        else:
            return 0

    @property
    def pages(self):
        if not self.count:
            return 0
        if self.count == self.items_per_page:
            return 1
        return (self.count // self.items_per_page) + 1

    def has_next(self):
        if self.pages > 1:
            if self.current_page < self.pages:
                return True
        return False

    @property
    def next(self):
        if self.has_next() and 0 < self.current_page < self.pages + 1:
            return self.current_page + 1
        return None

    def has_prev(self):
        if self.pages > 1:
            if self.current_page > 1:
                return True
        return False

    @property
    def prev(self):
        if self.has_prev() and 0 < self.current_page < self.pages + 1:
            return self.current_page - 1

    @property
    def page(self):
        index = self.current_page * self.items_per_page
        if not index:
            return None
        if self.query:
            try:
                order = list(self.query.query.order_by)
                order.append('id')
                return self.query.order_by(*order)[index - self.items_per_page:index]
            # Кастыль см. trello #170
            except AttributeError:
                return self.query.order_by('id')[index - self.items_per_page:index]
        if self.item_list:
            return self.item_list[index - self.items_per_page:index]
        if self.model:
            return self.model.objects.order_by('id')[index - self.items_per_page:index]

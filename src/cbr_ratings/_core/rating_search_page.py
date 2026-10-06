from cbr_ratings._core.cbr_api_model import CbrApiModel
from cbr_ratings._core.rating_item import RatingItem


class RatingSearchPage(CbrApiModel):
    page_count: int
    page_number: int
    sorting_field: str
    sorting_direction: str
    page_size: int
    item_list: list[RatingItem]
    item_count: int

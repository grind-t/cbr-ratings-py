from cbr_ratings._core.rating.rating_item import RatingItem
from cbr_ratings._core.shared.cbr_api_model import CbrApiModel


class RatingSearchPage(CbrApiModel):
    page_count: int
    page_number: int
    sorting_field: str
    sorting_direction: str
    page_size: int
    item_list: list[RatingItem]
    item_count: int

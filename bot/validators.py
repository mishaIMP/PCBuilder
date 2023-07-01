def validate_price_range(pr: str) -> bool:
    try:
        min_price, max_price = map(int, pr.split('-'))
        if min_price > max_price:
            raise
    except Exception as ex:
        print(ex)
        return False
    return True

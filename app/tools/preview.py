def calculate_cost(df):
    total = len(df)
    cost = round(total * 0.1, 2)

    return total, cost


def get_preview(df, page=0, page_size=10):
    start = page * page_size
    end = start + page_size
    return df.iloc[start:end].to_dict(orient="records")

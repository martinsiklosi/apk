import json


FILE_NAME = "fast_sortiment.json"
N_GOOD = 10
N_BAD = 5


def format_product(product: dict) -> str:
    return f"{product['AlcoholPerKrona']} ml/kr   {product['ArticleNumber']:5} {product['Name']:20} {product['Price'] + 'kr':8} {product['AlcoholPerVolume'] + '%':6} {product['Volume'] + 'ml':6} ({product['Tags'].split(',')[0]})"

def contains_alc(product: dict):
    return not "Alkoholfri" in product['Tags']


def main():
    with open(FILE_NAME) as file:
        products = json.load(file)

    products.sort(reverse=True, key=lambda product: product['AlcoholPerKrona'])
    products = list(filter(contains_alc, products))
    
    print()
    for product in products[:N_GOOD]:
        print(format_product(product))
    print(".\n.\n.")
    for product in products[-N_BAD:]:
        print(format_product(product))
    input("\nPress ENTER to exit...")


if __name__ == '__main__':
    main()
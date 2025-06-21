from django.shortcuts import render

def index(request):
    cars = [
        {"id": 1, "brand": "Toyota", "model": "Camry", "year": 2020, "description": "Надійний седан.", "image": "toyota.jpg"},
        {"id": 2, "brand": "BMW", "model": "X5", "year": 2019, "description": "Потужний кросовер.", "image": "bmw.jpg"},
        {"id": 3, "brand": "Tesla", "model": "Model S", "year": 2022, "description": "Електромобіль з автопілотом.", "image": "tesla.jpg"},
        {"id": 4, "brand": "Ford", "model": "Mustang", "year": 2018, "description": "Легендарний спорткар.", "image": "mustang.jpg"},
    ]
    return render(request, "car_index.html", {"cars": cars, "count": len(cars)})

def car_detail(request, id):
    cars = [
        {"id": 1, "brand": "Toyota", "model": "Camry", "year": 2020, "description": "Надійний седан.", "image": "toyota.jpg"},
        {"id": 2, "brand": "BMW", "model": "X5", "year": 2019, "description": "Потужний кросовер.", "image": "bmw.jpg"},
        {"id": 3, "brand": "Tesla", "model": "Model S", "year": 2022, "description": "Електромобіль з автопілотом.", "image": "tesla.jpg"},
        {"id": 4, "brand": "Ford", "model": "Mustang", "year": 2018, "description": "Легендарний спорткар.", "image": "mustang.jpg"},
    ]
    car = next((c for c in cars if c["id"] == id), None)
    if not car:
        return render(request, "404.html", status=404)
    return render(request, 'car_detail.html', {'car': car})
def car_gallery(request, id):
    cars = [
        {"id": 1, "brand": "Toyota", "model": "Camry"},
        {"id": 2, "brand": "BMW", "model": "X5"},
        {"id": 3, "brand": "Tesla", "model": "Model S"},
        {"id": 4, "brand": "Ford", "model": "Mustang"},
    ]
    car = next((c for c in cars if c["id"] == id), None)
    if not car:
        return render(request, "404.html", status=404)
    # Тестові фото для Toyota Camry
    photos = [
        {"title": "Camry Exterior", "description": "Зовнішній вигляд", "image": ""},
        {"title": "Camry Interior", "description": "Салон", "image": ""},
    ] if id == 1 else []
    return render(request, 'car_gallery.html', {'car': car, 'photos': photos})
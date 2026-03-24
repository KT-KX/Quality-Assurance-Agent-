def get_weather_advice(city):
    weather_data = {
        "Kuala Lumpur": {"temp": 32, "condition": "Sunny"},
        "Sepang": {"temp": 30, "condition": "Rainy"},
        "Xiamen": {"temp": 22, "condition": "Cloudy"}
    }
    
    city = city.strip().title()
    if city not in weather_data:
        return "Error: City not found."
    
    data = weather_data[city]
    if data['condition'] == "Rainy":
        return "Advice: Bring an umbrella."
    elif data['temp'] > 30:
        return "Advice: Stay hydrated!"
    return "Advice: Enjoy the day."

if _name_ == "_main_":
    print(get_weather_advice(input("Enter city: ")))

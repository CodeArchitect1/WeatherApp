import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import json
import os

USER_PREFS = "user_prefs.json"
def load_prefs():
    if os.path.exists(USER_PREFS):
        with open(USER_PREFS, 'r') as f:
            return json.load(f)
    else:
        return {"city": ""}

# Save user preferences
def save_prefs(prefs):
    with open(USER_PREFS, 'w') as f:
        json.dump(prefs, f)

def get_weather(city):
    api_key = "d3f4e3971fd27a078b119e592929aeff"
    base_url = "http://api.openweathermap.org/data/2.5/forecast?" # This is the 5 day forecast API

    complete_url = base_url + "appid=" + api_key + "&q=" + city + "&units=imperial"
    response = requests.get(complete_url)
    data = response.json()

    if data["cod"] == "200":
        forecast_data = data["list"]
        last_date = ""
        result_str = ""
        for day_data in forecast_data:
            dt_txt = day_data['dt_txt']
            date, time = dt_txt.split(' ')
            hour = int(time.split(':')[0])

            # Only add forecasts for 6AM, 12PM and 6PM
            if hour in [6, 12, 18]:
                if date != last_date:
                    result_str += f"\n\nDate: {date}\n"
                    last_date = date

                temperature = day_data["main"]["temp"]
                pressure = day_data["main"]["pressure"]
                humidity = day_data["main"]["humidity"]
                wind_speed = day_data["wind"]["speed"]
                wind_deg = day_data["wind"]["deg"]
                clouds = day_data["clouds"]["all"]
                rain = day_data.get("rain", {}).get("3h", 0)  # Get the amount of rain in the last 3 hours, if available
                snow = day_data.get("snow", {}).get("3h", 0)  # Get the amount of snow in the last 3 hours, if available
                weather_desc = day_data["weather"][0]["description"]
                result_str += f"Time: {hour}:00\nTemperature: {temperature}\nPressure: {pressure}\nHumidity: {humidity}\nWind Speed: {wind_speed}\nWind Direction: {wind_deg}\nCloudiness: {clouds}%\nRain (last 3 hours): {rain}mm\nSnow (last 3 hours): {snow}mm\nDescription: {weather_desc}\n\n"
    else:
        result_str = "Invalid city: Please check your city name or check your internet connection"

    return result_str

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        self.root.geometry("800x600")
        self.root.configure(bg="light blue")

        self.title_label = tk.Label(root, text="Weather Forecast App", font=("Helvetica", 24), bg="light blue")
        self.title_label.pack(pady=10)

        self.weather_icon = tk.PhotoImage(file='cloud.png')
        self.icon_label = tk.Label(root, image=self.weather_icon, bg="light blue")
        self.icon_label.pack(pady=10)

        self.city_name_var = tk.StringVar()
        self.city_entry = tk.Entry(root, textvariable=self.city_name_var, width=20, font=("Helvetica", 18))
        self.city_entry.pack(pady=10)

        self.result_text = tk.Text(root, bg="white", fg="black", font=("Helvetica", 16), height=20, width=80)
        self.result_text.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.scrollbar = tk.Scrollbar(root)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # attach text box to scrollbar
        self.scrollbar.config(command=self.result_text.yview)
        self.result_text.config(yscrollcommand=self.scrollbar.set)

        self.get_weather_button = tk.Button(root, text="Get Weather", command=self.display_weather, font=("Helvetica", 18), bg="sky blue")
        self.get_weather_button.pack(pady=10)

        self.refresh_weather()  # Start the auto-refresh
        self.auto_refresh_id = None
        
        self.prefs = load_prefs()
        self.city_name_var.set(self.prefs.get("city", ""))


    def display_weather(self):
        city = self.city_name_var.get()
        if city:  # Check if a city has been entered
            weather_data = get_weather(city)
            if "Invalid city" in weather_data:
                messagebox.showerror("Error", "Invalid city: Please check your city name or check your internet connection")
                self.city_entry.config(bg='red')
            else:
                # Save the city to the user preferences
                self.prefs["city"] = city
                save_prefs(self.prefs)
                
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, weather_data)
                self.city_entry.config(bg='white')
                if self.auto_refresh_id:
                    self.root.after_cancel(self.auto_refresh_id) # Cancel the previous auto-refresh
                self.auto_refresh_id = self.root.after(60000, self.refresh_weather) # Schedule the next refresh in 60 seconds
        else:
            self.city_entry.config(bg='white') # If no city is entered, set the entry field back to white

    def refresh_weather(self):
        city = self.city_name_var.get()
        if city:  # Only refresh the weather if a city has been entered
            self.display_weather()  # Refresh the weather


if __name__ == '__main__':
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()



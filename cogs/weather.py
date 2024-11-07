import discord
from discord.ext import commands
import requests

WEATHER_API_KEY = "YOUR_API_OPENWEATHER"

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def translate_weather_description(self, description):
        translations = {
            "haze": "Kabut Asap 🌫️",
            "clear sky": "Langit Cerah ☀️",
            "few clouds": "Sedikit Awan 🌤️",
            "scattered clouds": "Awan Tersebar ☁️",
            "broken clouds": "Awan Pecah ☁️",
            "shower rain": "Hujan Gerimis 🌧️",
            "rain": "Hujan 🌧️",
            "thunderstorm": "Badai Petir ⛈️",
            "snow": "Salju ❄️",
            "mist": "Kabut 🌫️"
        }
        return translations.get(description.lower(), description.capitalize())

    def get_weather_data(self, city):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    @commands.command(name='weather')
    async def weather(self, ctx, *, city: str):
        data = self.get_weather_data(city)
        if data:
            weather_desc = data['weather'][0]['description']
            translated_desc = self.translate_weather_description(weather_desc)
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            country = data['sys']['country']

            embed = discord.Embed(title=f"Cuaca di {city.title()}, {country}", color=discord.Color.green())
            embed.add_field(name="🌤️ Kondisi", value=translated_desc, inline=False)
            embed.add_field(name="🌡️ Temperatur", value=f"{temp}°C", inline=True)
            embed.add_field(name="🤗 Terasa Seperti", value=f"{feels_like}°C", inline=True)
            embed.add_field(name="💧 Kelembaban", value=f"{humidity}%", inline=True)
            embed.add_field(name="🌬️ Kecepatan Angin", value=f"{wind_speed} m/s", inline=True)
            embed.set_footer(text="Sumber: OpenWeatherMap")
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("Tidak dapat menemukan informasi cuaca untuk kota tersebut. Pastikan nama kota benar.")

async def setup(bot):
    await bot.add_cog(Weather(bot))

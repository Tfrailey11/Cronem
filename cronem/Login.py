from dotenv import load_dotenv
import os
from pathlib import Path
import json


env_path = Path.home() / ".cronem" / ".env"
load_dotenv(env_path)


username = os.getenv('CRONOMETER_USERNAME')
password= os.getenv('CRONOMETER_PASSWORD')



safe_user = json.dumps(username)
safe_password = json.dumps(password)

login_steps = f"""
        await page.goto('https://cronometer.com/login/')
        await page.waitForTimeout(3000)
        const loginTitle = await page.title()
        if (loginTitle !== 'Cronometer Login') {{
            await page.goto('https://cronometer.com/#custom-foods')
        }} else {{
            await page.fill('#username', {safe_user})
            await page.fill('#password', {safe_password})
            await page.click('#login-button')
            await page.waitForTimeout(3000)
            await page.goto('https://cronometer.com/#custom-foods')
        }}
        await page.waitForTimeout(3000)"""

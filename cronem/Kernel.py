from kernel import Kernel
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv
import os
from . import main
from . import Login


env_path = Path.home() / ".cronem" / ".env"
load_dotenv(env_path)

api_key = os.getenv("KERNEL_API_KEY")

kernel = Kernel(
        api_key = api_key,
        max_retries=0,
        timeout=120.0
        )

write_path = Path("stored_names.txt")
write_path.touch(exist_ok=True)

values = main.NumberedFoodInfo
values_json = json.dumps(values)

MainFoodName = main.FoodName
safe_name = json.dumps(MainFoodName)



addToDiary = None

with open('stored_names.txt', 'r') as file:
    lines = [line.strip() for line in file.readlines()]
    if MainFoodName in lines:
        print(f"{MainFoodName} has already been added as a custom food")
        addToDiary = True
    else:
        print(f"Adding {MainFoodName} as a custom food...")
        addToDiary = False
        with open('stored_names.txt', 'a') as write_file:
            write_file.write(f"{MainFoodName}\n")

login = Login.login_steps

if addToDiary:
    action_steps = f"""
        const searchInput = page.locator('input[placeholder="Search your foods..."]')
        await searchInput.fill({safe_name})
        await page.waitForTimeout(1500)

        await page.locator('div[role="button"]:has-text({safe_name})').click()
        await page.waitForTimeout(2000)

        const addToDiary = page.locator('button:has-text("ADD TO DIARY")')
        await addToDiary.waitFor({{ state:'visible', timeout:5000}})
        await addToDiary.click()
        await page.waitForTimeout(1000)

        const addToDiaryTwo = page.locator('button:has-text("ADD TO DIARY")').last()
        await addToDiaryTwo.waitFor({{ state: 'visible', timeout:5000 }})
        await addToDiaryTwo.click()
        await page.waitForTimeout(1000)

        return 'Existing food logged'
    """
else:

        action_steps = f"""await page.click('text=CREATE FOOD')
        await page.waitForTimeout(3000)

        const html = await page.locator('text=Food Name').first().evaluate(node => node.parentElement.outerHTML)
        
        const xpath = 'xpath=//div[contains(@class,"gwt-Label") and text()="Food Name"]' +
        '/following-sibling::div[1]//input'

        const nameInput = page.locator(xpath)
        await nameInput.click()
        await nameInput.fill('')
        await nameInput.pressSequentially({safe_name}, {{ delay:50}})

       

        const boxes = page.locator('.GHL1WBHBGJ.admin-edit-box')
        const values = {values_json}

        

        for (const[i, val] of Object.entries(values)) {{
            const input = boxes.nth(Number(i))
            const display = input.locator('xpath=preceding-sibling::div[1]')
            await display.click()
            await page.waitForTimeout(200)
            await input.fill(val)
            await page.keyboard.press('Tab')
            await page.waitForTimeout(200)
        }}

        const saveButton = page.locator('text=SAVE CHANGES')
        const addToDiary = page.locator('button:has-text("ADD TO DIARY")')
        await saveButton.waitFor({{state:'visible', timeout:5000 }})
        await saveButton.click()
        await addToDiary.waitFor({{ state:'visible', timeout:5000 }})
        await addToDiary.click()
        await page.waitForTimeout(1000)

        const addToDiaryTwo = page.locator('button:has-text("ADD TO DIARY")').last()
        await addToDiaryTwo.waitFor({{state:'visible', timeout:5000}})
        await addToDiaryTwo.click()
        await page.waitForTimeout(1000)

        return 'Saved and logged'"""

kernel_browser = kernel.browsers.create()

try:
    response = kernel.browsers.playwright.execute(
        id=kernel_browser.session_id,
        code=f"""

        {login}

        {action_steps}
        """)
    

    print("results: ", response.result)
    print('error: ', response.error)
    print('stderr: ', response.stderr)





except Exception as e:
    print(e)
finally:
    kernel.browsers.delete_by_id(kernel_browser.session_id)







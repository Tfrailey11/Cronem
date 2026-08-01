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

values = main.AllNumberedFoodInfo


Write_Names = list(values.keys())


FoodStatus = {}


for MainFoodName in Write_Names:


    with open('stored_names.txt', 'r') as file:
        lines = [line.strip() for line in file.readlines()]

        FullFoodName = f"{main.hall.title()} {MainFoodName}"

        if FullFoodName in lines:
            print(f"{FullFoodName} has already been added as a custom food")
            FoodStatus[MainFoodName] = True
        else:
            print(f"Adding {FullFoodName} as a custom food...")
            FoodStatus[MainFoodName] = False
            with open('stored_names.txt', 'a') as write_file:
                write_file.write(f"{FullFoodName}\n")

login = Login.login_steps


for food, exists in FoodStatus.items():
    print(f"=== Processing {food} ===")

    food_name = f"{main.hall.title()} {food}"
    food_json = json.dumps(food_name)

    food_values = values[food]
    values_json = json.dumps(food_values)
    if exists:
        action_steps = f"""
        const searchInput = page.locator('input[placeholder="Search your foods..."]')
        await searchInput.fill({food_json})
        await page.waitForTimeout(1500

        await page.locator('div[role="button"]:has-text({food_json})').click()
        await page.waitForTimeout(2000)

        const addToDiary = page.locator('button:has-text("ADD TO DIARY")')
        await addToDiary.waitFor({{ state:'visible', timeout:5000}})
        await addToDiary.click()
        await page.waitForTimeout(1000)

        const addToDiaryTwo = page.locator('button:has-text("ADD TO DIARY")').last()
        await addToDiaryTwo.waitFor({{ state: 'visible', timeout:5000 }})
        await addToDiaryTwo.click()
        await page.waitForTimeout(1000)

        const backButton = page.locator('text=BACK TO FOODS LIST')
        await backButton.waitFor({{state:'visible', timeout:5000}})
        await backButton.click()

        const createFoodButton = page.locator('text=CREATE FOOD')
        await createFoodButton.waitFor({{state:'visible', timeout:5000}})

        """
    else:
        action_steps = f"""
            console.log("About to create: ", {food_json})
            console.log(await page.url)

            await page.click('text=CREATE FOOD')
            await page.waitForTimeout(3000)

            const html = await page.locator('text=Food Name')
            .first().evaluate(node => node.parentElement.outerHTML)

            const xpath = 'xpath=//div[contains(@class,"gwt-Label") and text()="Food Name"]' +
            '/following-sibling::div[1]//input'

            const nameInput = page.locator(xpath)
            await nameInput.click()
            await nameInput.fill('')
            await nameInput.pressSequentially({food_json}, {{ delay:50}})



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

            const backButton = page.locator('text=BACK TO FOODS LIST')
            await backButton.waitFor({{state:'visible', timeout:5000}})
            await backButton.click()

            const createFoodButton = page.locator('text=CREATE FOOD')
            await createFoodButton.waitFor({{state:'visible', timeout:5000}})

            """

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







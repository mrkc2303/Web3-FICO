const puppeteer = require("puppeteer");
const fs = require("fs");

async function scrapeEthereumAddresses(url) {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  let allAddresses = [];

  try {
    await page.goto(url, { waitUntil: "networkidle2" });

    let hasNextPage = true;

    while (hasNextPage) {
      // Wait for the table to load
      await page.waitForSelector("table.mantine-datatable-table");

      // Extract Ethereum addresses from the current page
      const ethereumAddresses = await page.evaluate(() => {
        const rows = Array.from(
          document.querySelectorAll("table.mantine-datatable-table tbody tr")
        );
        const ethAddresses = [];

        rows.forEach((row) => {
          const networkCell = row.querySelector("td:nth-child(2)");
          const addressCell = row.querySelector("td:nth-child(1)");

          if (
            networkCell &&
            addressCell &&
            networkCell.innerText.includes("Ethereum")
          ) {
            ethAddresses.push(addressCell.innerText.trim());
          }
        });

        return ethAddresses;
      });

      // Add the addresses to the overall list
      allAddresses = allAddresses.concat(ethereumAddresses);

      // Check if there's a next page and navigate to it
      const nextPageButton = await page.$('button[aria-label="Next page"]');
      if (nextPageButton) {
        const isDisabled = await page.evaluate(
          (button) => button.disabled,
          nextPageButton
        );
        if (isDisabled) {
          hasNextPage = false; // No more pages to navigate
        } else {
          await nextPageButton.click(); // Go to the next page
        //   await page.waitForTimeout(2000); // Wait for the page to load
          await new Promise((resolve) => setTimeout(resolve, 2000));
        }
      } else {
        hasNextPage = false; // If no button is found
      }
    }

    fs.writeFileSync("ethereum_addresses.json", JSON.stringify(allAddresses, null, 2));
    const csvData = allAddresses.map((address) => `${address}`).join("\n");
    fs.writeFileSync("ethereum_addresses.csv", csvData);
    
    console.log("Data exported to ethereum_addresses.json and ethereum_addresses.csv");
    
    console.log("All Ethereum Addresses:", allAddresses);
    return allAddresses;
  } catch (error) {
    console.error("Error scraping Ethereum addresses:", error);
    return [];
  } finally {
    await browser.close();
  }
}

// Example usage
const url = "https://checkcryptoaddress.com/scam-wallets";
scrapeEthereumAddresses(url);
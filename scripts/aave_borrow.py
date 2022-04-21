from brownie import config, network, interface
from scripts.helper_scrips import get_account, FORKED_LOCAL_ENVIRONMENTS
from scripts.get_weth import get_weth
from web3 import Web3

AMOUNT = 0.1


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]
        ["lending_pool_addresses_provider"], )
    lending_pool_adddress = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_adddress)
    return lending_pool


def approve_erc20(amount, spender, erc20_address, account):
    print("Approving ERC20...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved ERC20")
    return tx


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        _,  # current_liquidation_threshold
        _,  # ltv
        _,  # helth_factor
    ) = lending_pool.getUserAccountData(account.address)
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    print(f"Total Collateral: {total_collateral_eth} ETH")
    print(f"Total Debt: {total_debt_eth} ETH")
    print(f"Available Borrow: {available_borrow_eth} ETH")
    return (float(available_borrow_eth), float(total_debt_eth))


def get_asset_price(price_feed_address):
    price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"Price DAI/ETH is {converted_latest_price}")
    return float(converted_latest_price)


def repay_borrowed(token, amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    repay_tx = lending_pool.repay(
        token,
        amount,
        1,
        account,
        {"from": account},
    )
    repay_tx.wait(1)
    print("Repaid borrowed Asset!")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in FORKED_LOCAL_ENVIRONMENTS:
        get_weth()
    lending_pool = get_lending_pool()
    # Approve sending our ERC20 token
    approve_erc20(
        Web3.toWei(AMOUNT, "ether"),
        lending_pool.address,
        erc20_address,
        account,
    )
    print("Depositing....")
    tx = lending_pool.deposit(
        erc20_address,
        Web3.toWei(AMOUNT, "ether"),
        account.address,
        0,
        {"from": account},
    )
    tx.wait(1)
    print("Deposited!")
    # how much can we borrow?
    (borrowable_eth, total_debt) = get_borrowable_data(lending_pool, account)
    print("Borrowing....")
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"])
    amount_dai_to_borrow = (borrowable_eth * 0.95) / dai_eth_price
    print(f"We are going to borrow {amount_dai_to_borrow} DAI")
    # Now we will borrow
    dai_token_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_token_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,  # Interest Rate: 1 - Stable, 2 - Variable
        0,  # Referal codes no longer exist so 0
        account,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("Borrowed some DAI from Aave!")
    get_borrowable_data(lending_pool, account)
    repay_borrowed(
        dai_token_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        lending_pool,
        account,
    )

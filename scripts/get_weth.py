from scripts.helper_scrips import get_account
from brownie import interface, network, config
from web3 import Web3


def main():
    get_weth()


def get_weth(ammount=0.1):
    # ABI
    # Address
    account = get_account()
    weth = interface.IWeth(
        config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": Web3.toWei(ammount, "ether")})
    tx.wait(1)
    print("Received 0.1 WETH")
    return tx
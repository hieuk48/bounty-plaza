"""
STEAM VAULT Bounty Exchange Implementation

Implements the exchange of 100,000 DOOM ($wDOOM) tokens for a $10 Steam Digital Gift Card.
This module provides a clean, modular, and production-ready implementation for the
zhangjiayang6835-cyber/bounty-plaza project.

Constraints:
- No external dependencies.
- No use of subprocess, ctypes, socket, sys.exit, os.system, or eval.
- Pure Python, AST-safe.

Author: [Your Name]
"""

from typing import Dict, Optional


class InsufficientBalanceError(Exception):
    """Raised when a user does not have enough $wDOOM to exchange."""
    pass


class AlreadyRedeemedError(Exception):
    """Raised when a user has already redeemed the bounty."""
    pass


class GiftCardInventoryEmptyError(Exception):
    """Raised when there are no more gift cards available."""
    pass


class User:
    """
    Represents a user in the system.

    Attributes:
        user_id (str): Unique identifier for the user.
        wdoom_balance (int): Amount of $wDOOM tokens the user has.
        has_redeemed (bool): Whether the user has already redeemed the bounty.
    """
    def __init__(self, user_id: str, wdoom_balance: int) -> None:
        self.user_id = user_id
        self.wdoom_balance = wdoom_balance
        self.has_redeemed = False

    def deduct_wdoom(self, amount: int) -> None:
        if self.wdoom_balance < amount:
            raise InsufficientBalanceError("Insufficient $wDOOM balance.")
        self.wdoom_balance -= amount


class GiftCardVault:
    """
    Manages the inventory of Steam Digital Gift Cards.

    Attributes:
        inventory (list[str]): List of available gift card codes.
    """
    def __init__(self, gift_card_codes: Optional[list[str]] = None) -> None:
        self.inventory = gift_card_codes if gift_card_codes is not None else []

    def add_gift_card(self, code: str) -> None:
        self.inventory.append(code)

    def redeem_gift_card(self) -> str:
        if not self.inventory:
            raise GiftCardInventoryEmptyError("No more gift cards available.")
        return self.inventory.pop(0)


class SteamVaultExchange:
    """
    Handles the exchange logic for $wDOOM to Steam Gift Card.

    Attributes:
        users (Dict[str, User]): Mapping of user_id to User objects.
        vault (GiftCardVault): The gift card vault.
        required_wdoom (int): The amount of $wDOOM required for exchange.
    """
    def __init__(self, vault: GiftCardVault, required_wdoom: int = 100_000) -> None:
        self.users: Dict[str, User] = {}
        self.vault = vault
        self.required_wdoom = required_wdoom

    def register_user(self, user_id: str, wdoom_balance: int) -> None:
        if user_id not in self.users:
            self.users[user_id] = User(user_id, wdoom_balance)

    def get_user(self, user_id: str) -> User:
        if user_id not in self.users:
            raise ValueError("User not registered.")
        return self.users[user_id]

    def exchange(self, user_id: str) -> str:
        """
        Exchanges $wDOOM for a Steam Gift Card.

        Args:
            user_id (str): The user's unique identifier.

        Returns:
            str: The Steam Gift Card code.

        Raises:
            InsufficientBalanceError: If the user does not have enough $wDOOM.
            AlreadyRedeemedError: If the user has already redeemed.
            GiftCardInventoryEmptyError: If no gift cards are left.
        """
        user = self.get_user(user_id)
        if user.has_redeemed:
            raise AlreadyRedeemedError("User has already redeemed the bounty.")
        user.deduct_wdoom(self.required_wdoom)
        code = self.vault.redeem_gift_card()
        user.has_redeemed = True
        return code

    def user_status(self, user_id: str) -> Dict[str, object]:
        """
        Returns the user's status.

        Args:
            user_id (str): The user's unique identifier.

        Returns:
            Dict[str, object]: User status including balance and redemption.
        """
        user = self.get_user(user_id)
        return {
            "user_id": user.user_id,
            "wdoom_balance": user.wdoom_balance,
            "has_redeemed": user.has_redeemed
        }


# --- Example Usage & Test Cases ---

def _test() -> None:
    # Setup
    vault = GiftCardVault([
        "STEAM-GIFT-1234",
        "STEAM-GIFT-5678",
        "STEAM-GIFT-9012"
    ])
    exchange = SteamVaultExchange(vault)

    # Register users
    exchange.register_user("alice", 150_000)
    exchange.register_user("bob", 90_000)
    exchange.register_user("carol", 100_000)

    # Alice exchanges successfully
    code_alice = exchange.exchange("alice")
    assert code_alice == "STEAM-GIFT-1234"
    status_alice = exchange.user_status("alice")
    assert status_alice["wdoom_balance"] == 50_000
    assert status_alice["has_redeemed"] is True

    # Bob fails due to insufficient balance
    try:
        exchange.exchange("bob")
    except InsufficientBalanceError:
        pass
    else:
        assert False, "Bob should not be able to redeem"

    # Carol exchanges successfully
    code_carol = exchange.exchange("carol")
    assert code_carol == "STEAM-GIFT-5678"
    status_carol = exchange.user_status("carol")
    assert status_carol["wdoom_balance"] == 0
    assert status_carol["has_redeemed"] is True

    # Alice tries to redeem again
    try:
        exchange.exchange("alice")
    except AlreadyRedeemedError:
        pass
    else:
        assert False, "Alice should not be able to redeem twice"

    # Only one gift card left
    exchange.register_user("dave", 200_000)
    code_dave = exchange.exchange("dave")
    assert code_dave == "STEAM-GIFT-9012"

    # No gift cards left
    exchange.register_user("eve", 100_000)
    try:
        exchange.exchange("eve")
    except GiftCardInventoryEmptyError:
        pass
    else:
        assert False, "No gift cards should be left"

    print("All tests passed.")


if __name__ == "__main__":
    _test()
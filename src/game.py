import asyncio
from dataclasses import dataclass
import select
import sys

from connect import Twitch, YouTube


TWITCH_CHANNEL = "nqdoms" 
STREAMING_ON_TWITCH = True
YOUTUBE_CHANNEL_ID = "nqdoms" 
YOUTUBE_STREAM_URL = None
MESSAGE_RATE = 1


@dataclass
class Message:
    username: str
    content: str


@dataclass
class Turn:
    username: str
    elo: int


@dataclass
class Guesser:
    guesses: list[int]
    scores: list[int]
    current_guess: int = 0
    current_score: int = 1000

    @classmethod
    def create(cls, turns: int):
        return cls(
            guesses=[0] * turns,
            scores=[1000] * turns
        )

    def update(self, turn, elo, guess):
        self.guesses[turn] = self.current_guess = guess
        self.scores[turn] = abs(elo - guess)

    def update_turn(self, turn):
        self.current_score = sum(self.scores[:turn + 1])


class Game:

    def __init__(self, service: Twitch | YouTube, turns: list[Turn]):
        self.service = service
        self.turns = turns
        self.turn_count = len(self.turns)
        self.turn = 0
        self.guessers: dict[str, Guesser] = {}
        self.med_guesser = Guesser.create(self.turn_count)
        self.active = False

    async def game_loop(self):
        if not self.active:
            return

        new_messages = [
            Message(message["username"].lower(), message["message"].lower())
            for message in self.service.receive_messages()
        ]
        if not new_messages:
            return
        print(f"Received {len(new_messages)} new messages")
        for message in new_messages:
            guess = self.parse_guess(message.content)
            if not guess:
                continue

            if message.username not in self.guessers:
                self.guessers[message.username] = Guesser.create(self.turn_count)

            self.guessers[message.username].update(self.turn, self.turns[self.turn].elo, guess)

    async def end_round(self):
        print(f"Current guessers:")
        for username, guesser in self.guessers.items():
            guesser.update_turn(self.turn)
            print(f"{username}: {guesser.current_score}")
        self.active = False

    async def new_round(self):
        self.turn += 1
        if self.turn >= self.turn_count:
            print(f"Ending game")
            exit()

        print(f"Starting round {self.turn}")
        self.active = True

    def parse_guess(self, message: str) -> int | None:
        if not message.isnumeric():
            return None
        guess = int(message)
        if not 500 <= guess <= 2500:
            return None
        return guess


async def entry_point():
    for i in range(3, 0, -1):
        print(f"Starting in {i}...",  end="\r")
        await asyncio.sleep(1)

    if STREAMING_ON_TWITCH:
        service = Twitch()
        service.twitch_connect(TWITCH_CHANNEL)
    else:
        service = YouTube()
        service.youtube_connect(YOUTUBE_CHANNEL_ID, YOUTUBE_STREAM_URL)

    # Dummy turns for demonstration, replace with your actual turns
    turns = [Turn(username="player1", elo=1200), Turn(username="player2", elo=1500)]
    game = Game(service, turns)
    game.active = True

    while True:
        await game.game_loop()
        await asyncio.sleep(0.4)
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            sys.stdin.readline()
            if game.active:
                await game.end_round()
            else:
                await game.new_round()


if __name__ == "__main__":
    asyncio.run(entry_point())

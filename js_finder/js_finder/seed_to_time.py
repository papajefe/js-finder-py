"""Seed to Time module for pyodide to access"""
import sys
import numba_pokemon_prngs


def main():
    """Main function to be run for the seed_to_time module"""
    lcrng = numba_pokemon_prngs.lcrng.PokeRNGDiv(0x12345678)
    print("Hello from seed to time!")
    print(f"{lcrng.next()=:08X}")
    print(f"{sys.version=}")

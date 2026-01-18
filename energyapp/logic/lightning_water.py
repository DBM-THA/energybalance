# berechnungen.py
from .models import Energy, Water, Building

def calc_energy(building: Building) -> dict:
    """
    Berechnet die Energie für alle Räume eines Gebäudes.
    Rückgabe: Dictionary mit Summen und pro-Raum-Werten
    """
    energies = Energy.objects.filter(building=building)

    total_power = 0
    total_hours = 0
    total_energy = 0
    room_results = []

    for e in energies:
        # Berechnung je Raum
        power = (e.area * e.esoll) / e.lm if e.lm != 0 else 0
        hours = e.volllast * e.days
        energy = power * hours / 1000  # kWh/a

        # Werte in Model speichern
        e.power = power
        e.hours = hours
        e.energy_consumption = energy
        e.save()

        # Summe
        total_power += power
        total_hours += hours
        total_energy += energy

        room_results.append({
            "room": e.room,
            "power": power,
            "hours": hours,
            "energy": energy
        })

    kwh_m2 = total_energy / sum([e.area for e in energies]) if energies else 0

    return {
        "total_power": total_power,
        "total_hours": total_hours,
        "total_energy": total_energy,
        "kwh_m2": kwh_m2,
        "rooms": room_results
    }


def calc_water(building: Building) -> dict:
    """
    Berechnet den Wasserbedarf für alle Räume eines Gebäudes.
    Rückgabe: Dictionary mit Summen und pro-Raum-Werten
    """
    waters = Water.objects.filter(building=building)

    total = 0
    room_results = []

    for w in waters:
        ep = w.dp * w.persons * 365
        ea = w.area * w.da * 365 / 1000
        em = (ep + ea) / 2

        w.ep = ep
        w.ea = ea
        w.em = em
        w.save()

        total += em

        room_results.append({
            "room": w.room,
            "ep": ep,
            "ea": ea,
            "em": em
        })

    avg_per_room = total / len(waters) if waters else 0

    return {
        "total_water": total,
        "avg_per_room": avg_per_room,
        "rooms": room_results
    }


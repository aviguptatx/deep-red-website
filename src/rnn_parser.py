import json
import re


def load_game(input):
    """
    Loads game information from a JSON string and populates the input layer of the LSTM

    Parameters
    ----------
    input : str
       JSON string representing a game to be parsed and converted to input layer

    Returns
    -------
    list
        List of containing one element: the data for this game
    """

    game_data = []
    game_outed = [0] * 7
    game_hitler = [0] * 7
    game_cnh = [0] * 7
    confirmed = [0] * 7

    lib_cards_played = 0
    fas_cards_played = 0

    data = json.loads(input)

    # Encode network's seat
    for seat in range(0, 7):
        if data["players"][seat]["role"] == "liberal":
            confirmed[seat] = 1
            confirmed_seat = seat

    # Length 8 (1-7 - investigated seat number) (8 - result)
    investigation_data = [0] * 8
    # Length 7 (1-7 - chosen seat number)
    special_election_data = [0] * 7
    # Length 7 (1-7 - shot seat number)
    bullet_data_1 = [0] * 7
    # Length 7 (1-7 - shot seat number)
    bullet_data_2 = [0] * 7

    # For each government
    for gov in range(0, len(data["logs"])):
        # If a veto forces a td
        veto_and_td = False
        # Lenth 31 (1-7 - pres, 8-14 chanc, 15-18 pres claim, 19-21 chanc claim, 22 veto, 23 blue, 24 red, 25-31 vote data)
        gov_data = []
        # Topdeck data
        topdeck = []

        # If the government was played
        if len(data["logs"][gov]) >= 5:
            # President seat number
            for pres in range(0, 7):
                gov_data.append(1 if data["logs"][gov]["presidentId"] == pres else 0)

            # Chancellor seat number
            for chan in range(0, 7):
                gov_data.append(1 if data["logs"][gov]["chancellorId"] == chan else 0)

            pres_claim = data["logs"][gov]["presidentClaim"]["reds"]
            chanc_claim = data["logs"][gov]["chancellorClaim"]["reds"]

            # President number of reds claimed
            if "presidentClaim" in data["logs"][gov]:
                gov_data.append(1 if pres_claim == 0 else 0)
                gov_data.append(1 if pres_claim == 1 else 0)
                gov_data.append(1 if pres_claim == 2 else 0)
                gov_data.append(1 if pres_claim == 3 else 0)

            # Chancellor number of reds claimed
            if "chancellorClaim" in data["logs"][gov]:
                gov_data.append(1 if chanc_claim == 0 else 0)
                gov_data.append(1 if chanc_claim == 1 else 0)
                gov_data.append(1 if chanc_claim == 2 else 0)

            # Encode card outed
            if (
                (
                    confirmed_seat == data["logs"][gov]["presidentId"]
                    or confirmed_seat == data["logs"][gov]["chancellorId"]
                )
                and (pres_claim - chanc_claim != 1 and pres_claim != 0)
                and "enactedPolicy" in data["logs"][gov]
                and data["logs"][gov]["enactedPolicy"] == "fascist"
            ):
                game_outed[
                    data["logs"][gov][
                        "chancellorId"
                        if confirmed_seat == data["logs"][gov]["presidentId"]
                        else "presidentId"
                    ]
                ] = 1

            # Veto
            gov_data.append(
                1
                if (
                    "presidentVeto" in data["logs"][gov]
                    and "chancellorVeto" in data["logs"][gov]
                    and data["logs"][gov]["presidentVeto"]
                    and data["logs"][gov]["chancellorVeto"]
                )
                else 0
            )

            # Enacted policy
            if "enactedPolicy" in data["logs"][gov]:
                gov_data.append(
                    0 if data["logs"][gov]["enactedPolicy"] == "fascist" else 1
                )
                gov_data.append(
                    1 if data["logs"][gov]["enactedPolicy"] == "fascist" else 0
                )
            else:
                gov_data.append(0)
                gov_data.append(0)

            # Vote data
            for seat in range(0, 7):
                gov_data.append(1 if data["logs"][gov]["votes"][seat] else 0)

            # If investigation
            if "investigationId" in data["logs"][gov]:
                investigation_data[data["logs"][gov]["investigationId"]] = 1
                investigation_data[7] = (
                    1 if data["logs"][gov]["investigationClaim"] == "fascist" else 0
                )

            # Encode inv outed
            if (
                "investigationId" in data["logs"][gov]
                and (
                    confirmed_seat == data["logs"][gov]["presidentId"]
                    or confirmed_seat == data["logs"][gov]["investigationId"]
                )
                and data["logs"][gov]["investigationClaim"] == "fascist"
            ):
                game_outed[
                    data["logs"][gov][
                        "investigationId"
                        if confirmed_seat == data["logs"][gov]["presidentId"]
                        else "presidentId"
                    ]
                ] = 1

            # Encode inv confirmed
            if (
                "investigationId" in data["logs"][gov]
                and confirmed_seat == data["logs"][gov]["presidentId"]
                and data["logs"][gov]["investigationClaim"] == "liberal"
            ):
                confirmed[data["logs"][gov]["investigationId"]] = 1

            # Did a veto force a topdeck
            if (
                "presidentVeto" in data["logs"][gov]
                and "chancellorVeto" in data["logs"][gov]
                and data["logs"][gov]["presidentVeto"]
                and data["logs"][gov]["chancellorVeto"]
                and "enactedPolicy" in data["logs"][gov]
            ):
                veto_and_td = True

            # If Special Election
            if "specialElection" in data["logs"][gov]:
                special_election_data[data["logs"][gov]["specialElection"]] = 1

            # If bullet
            if "execution" in data["logs"][gov]:
                # If first bullet
                if not 1 in bullet_data_1:
                    bullet_data_1[data["logs"][gov]["execution"]] = 1
                # If second bullet
                else:
                    bullet_data_2[data["logs"][gov]["execution"]] = 1

        # Neined government
        else:
            # President seat number
            for pres in range(0, 7):
                gov_data.append(1 if data["logs"][gov]["presidentId"] == pres else 0)

            # Chancellor seat number
            for chan in range(0, 7):
                gov_data.append(1 if data["logs"][gov]["chancellorId"] == chan else 0)

            # Empty data
            for fill in range(8):
                gov_data.append(0)

            # Encode enacted policy if topdecked
            if "enactedPolicy" in data["logs"][gov]:
                gov_data.append(
                    0 if data["logs"][gov]["enactedPolicy"] == "fascist" else 1
                )
                gov_data.append(
                    1 if data["logs"][gov]["enactedPolicy"] == "fascist" else 0
                )
            else:
                gov_data.append(0)
                gov_data.append(0)

            # Vote data
            for seat in range(0, 7):
                gov_data.append(1 if data["logs"][gov]["votes"][seat] else 0)

        # If the government was a topdeck
        if (
            len(data["logs"][gov]) == 4 and ("enactedPolicy" in data["logs"][gov])
        ) or veto_and_td:
            topdeck.append(1)
        else:
            topdeck.append(0)

        # If Hitler was elected in HZ
        if (
            len(data["logs"][gov]) == 4
            and "hitler" in data["logs"][gov]
            and fas_cards_played >= 3
        ):
            game_outed[data["logs"][gov]["chancellorId"]] = 1
            game_hitler[data["logs"][gov]["chancellorId"]] = 1

        # If Hitler was shot at any point
        if "execution" in data["logs"][gov] and "hitler" in data["logs"][gov]:
            game_outed[data["logs"][gov]["execution"]] = 1
            game_hitler[data["logs"][gov]["execution"]] = 1

        # Encode chancellors in HZ being CNH
        if len(data["logs"][gov]) >= 5 and fas_cards_played >= 3:
            game_cnh[data["logs"][gov]["chancellorId"]] = 1

        # All the people confirmed lib are also CNH, for example after inv
        for seat in range(7):
            game_cnh[seat] = game_cnh[seat] | confirmed[seat]

        if "enactedPolicy" in data["logs"][gov]:
            if data["logs"][gov]["enactedPolicy"] == "fascist":
                fas_cards_played += 1
            else:
                lib_cards_played += 1

        # Fill empty data with 0s
        for i in range(len(gov_data), 31):
            gov_data.append(0)

        game_data.append(
            gov_data
            + investigation_data
            + special_election_data
            + bullet_data_1
            + bullet_data_2
            + topdeck
            + confirmed
            + game_outed
            + game_hitler
            + game_cnh
        )

    return [game_data]


def convert_plaintext_to_json(input):
    """
    Takes a input containing plaintext game notation and converts it to a JSON string that can then be interpreted by load_game()

    Example:

    SEAT 1
    1111111 - 15 RRB RB B

    This method will take that game notation and convert it to a JSON string containing the following, which can be interpreted by load_game()

    {"logs": [{"votes": [true, true, true, true, true, true, true], "presidentId": 0, "chancellorId": 4, "presidentClaim": {"reds": 2, "blues": 1}, "chancellorClaim": {"reds": 1, "blues": 1}, "enactedPolicy": "liberal"}],
    "players": [{"role": "liberal"}, {"role": "not_me"}, {"role": "not_me"}, {"role": "not_me"}, {"role": "not_me"}, {"role": "not_me"}, {"role": "not_me"}]}

    Parameters
    ----------
    input : str
        Plaintext to be parsed and converted to JSON string

    Returns
    -------
    str
        JSON string representing a game to be parsed and converted to input layer
    """

    data = {}
    data["logs"] = []

    lines = input.splitlines()

    # Create players list that stores my_seat as liberal
    my_seat_index = int(re.split("SEAT", lines[0])[1]) - 1
    data["players"] = []
    for seat in range(7):
        seat_data = {}
        seat_data["role"] = "liberal" if seat == my_seat_index else "not_me"
        data["players"].append(seat_data)

    # Create government logs
    for line in lines[1:]:
        # Create dict to represent this government
        gov = {}
        # Votes list
        gov["votes"] = list(re.split(" - ", line)[0])
        # Convert to boolean
        for seat in range(7):
            gov["votes"][seat] = gov["votes"][seat] == "1"

        # President and chancellor Ids
        gov["presidentId"] = int(re.split(" - ", line)[1][0]) - 1
        gov["chancellorId"] = int(re.split(" - ", line)[1][1]) - 1

        # If the gov was played
        if len(line) > 15:
            # President claim
            reds = re.split(" - ", line)[1].split()[1].count("R")
            # Create dict
            gov["presidentClaim"] = {}
            # Number of reds and blues claimed
            gov["presidentClaim"]["reds"] = reds
            gov["presidentClaim"]["blues"] = 3 - reds

            # Chancellor claim
            reds = re.split(" - ", line)[1].split()[2].count("R")
            # Create dict
            gov["chancellorClaim"] = {}
            # Number of reds and blues claimed
            gov["chancellorClaim"]["reds"] = reds
            gov["chancellorClaim"]["blues"] = 2 - reds

            # Enacted policy
            policy = re.split(" - ", line)[1].split()[3]
            gov["enactedPolicy"] = "fascist" if policy == "R" else "liberal"

            # If a special action (inv, se, bullet) was taken or veto took place
            if line.count("-") == 2:
                # If investigation
                if "INV" in line:
                    gov["investigationId"] = (
                        int(re.split(" - ", line)[2].split()[1]) - 1
                    )
                    gov["investigationClaim"] = (
                        "liberal"
                        if re.split(" - ", line)[2].split()[2] == "LIB"
                        else "fascist"
                    )

                # If special election
                if "SE" in line:
                    gov["specialElection"] = (
                        int(re.split(" - ", line)[2].split()[1]) - 1
                    )

                # If bullet
                if "KILL" in line:
                    gov["execution"] = int(re.split(" - ", line)[2].split()[1]) - 1

                if "VETO" in line:
                    gov["presidentVeto"] = True
                    gov["chancellorVeto"] = True

        # Check if this gov was a topdeck
        elif len(line) == 15:
            policy = re.split(" - ", line)[1].split()[1]
            gov["enactedPolicy"] = "fascist" if policy == "R" else "liberal"

        if "H" in line:
            gov["hitler"] = True

        # Append this gov to the data
        data["logs"].append(gov)

    return json.dumps(data)

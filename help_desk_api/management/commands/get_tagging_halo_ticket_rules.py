import json
import pathlib
from collections import defaultdict
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand
from halo.halo_api_client import HaloAPIClient

from help_desk_api.models import HelpDeskCreds


class Command(BaseCommand):
    help = "Get Halo ticket rules that add a single tag and no more"  # /PS-IGNORE

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-c",
            "--credentials",
            type=str,
            help="Email address linked to Zendesk and Halo credentials",
        )
        parser.add_argument("-f", "--fields", type=pathlib.Path, help="Input fields file path")
        parser.add_argument("-r", "--rules", type=pathlib.Path, help="Input rules file path")
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def has_only_one_outcome(self, rule):
        return len(rule.get("outcomes", [])) == 1

    def has_only_one_criterion(self, rule):
        return len(rule.get("criteria", [])) == 1

    def sole_outcome_adds_tag(self, rule):
        outcome = rule["outcomes"][0]
        return outcome["fieldname"] == "tags"

    def filter_potentially_unnecessary_rules(self, rules):
        sole_criterion_rules = filter(self.has_only_one_criterion, rules)
        single_outcome_rules = filter(self.has_only_one_outcome, sole_criterion_rules)
        unnecessary_tag_rules = filter(self.sole_outcome_adds_tag, single_outcome_rules)
        return unnecessary_tag_rules

    def make_rule_make_sense(self, rule):
        criterion_fieldname = rule["criteria"][0]["fieldname"]
        criterion_value = rule["criteria"][0]["value_string"]
        field_data = self.fields_by_name.get(criterion_fieldname)
        if field_data and "values" in field_data:
            field_value = list(
                filter(lambda value: str(value["id"]) == str(criterion_value), field_data["values"])
            )
            if field_value:
                criterion_value = field_value[0]["name"]
        outcome_fieldname = rule["outcomes"][0]["fieldname"]
        outcome_value = rule["outcomes"][0]["value_string"]
        return (
            f"\t{rule['id']} - {rule['name']}:\n\t\tIF {criterion_fieldname} "
            f"IS {criterion_value} THEN ADD {outcome_value} TO {outcome_fieldname}\n"
        )

    def arrange_fields_by_name(self, fields):
        return {field["name"]: field for field in fields}

    fields_by_name = None

    def handle(self, *args, **options):
        halo_rules_data = None
        halo_fields_data = None
        input_rules_path = options["rules"]
        input_fields_path = options["fields"]
        credentials = None
        if input_rules_path and input_fields_path:
            # load rules file
            with open(input_rules_path, "r", encoding="utf-8-sig") as input_file:
                halo_rules_data = json.load(input_file)
            # load fields file
            with open(input_fields_path, "r", encoding="utf-8-sig") as input_file:
                halo_fields_data = json.load(input_file)
        elif options["credentials"] is not None:
            credentials = HelpDeskCreds.objects.get(zendesk_email=options["credentials"])
        else:
            raise ValueError("No Halo credentials supplied")

        halo_client = HaloAPIClient(
            client_id=credentials.halo_client_id, client_secret=credentials.halo_client_secret
        )

        halo_rules_data = halo_client.get("TicketRules")
        halo_fields_data = halo_client.get("FieldInfo?includevalues=true")  # /PS-IGNORE

        if not all([halo_rules_data, halo_fields_data]):
            self.stdout.write("Provide input file path or API credentials to get rules and fields")

        self.fields_by_name = self.arrange_fields_by_name(halo_fields_data)

        filtered_rules = list(self.filter_potentially_unnecessary_rules(halo_rules_data))
        filtered_rule_ids = [
            filtered_rule["id"]
            for filtered_rule in filtered_rules
            if (filtered_rule["active"]) and (filtered_rule["id"] != 957)
        ]
        wanted_rule_ids = [
            halo_rules_datum["id"]
            for halo_rules_datum in halo_rules_data
            if halo_rules_datum["id"] not in filtered_rule_ids
        ]
        # TODO: group by criterion field name
        #  to make it clearer which are just custom field weirdness

        # output = [self.make_rule_make_sense(rule) for rule in filtered_rules]
        rule_count, output = self.group_by_criterion_field(filtered_rules)

        print(f"Rules to disable: {len(filtered_rule_ids)}")
        print(f"Rules to enable: {len(wanted_rule_ids)}")

        for rule_to_disable in filtered_rule_ids:
            disablement = {
                "id": rule_to_disable,
                "active": False,
            }
            halo_client.post("TicketRules", payload=[disablement])

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(
                    timestamp=datetime.utcnow().isoformat(),
                )
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8-sig") as output_file:
                # json.dump(output, output_file, indent=4)
                for field, rules in output.items():
                    output_file.write(f"{field}\n")
                    output_file.writelines(rules)
        else:
            json.dump(output, self.stdout, indent=4)

    def group_by_criterion_field(self, filtered_rules):
        grouped = defaultdict(list)
        rule_count = 0
        for rule in filtered_rules:
            criterion_fieldname = rule["criteria"][0]["fieldname"]
            # grouped[criterion_fieldname] = grouped.setdefault(grouped[criterion_fieldname], [])
            grouped[criterion_fieldname].append(self.make_rule_make_sense(rule))
            rule_count += 1
        # rule_count = sum(grouped.values())
        return rule_count, grouped

    def group_by_name(self, filtered_rules):
        grouped = {}
        for rule in filtered_rules:
            criterion_fieldname = rule["name"]
            grouped[criterion_fieldname] = grouped.setdefault(criterion_fieldname, 0) + 1
        rule_count = sum(grouped.values())
        return rule_count, grouped

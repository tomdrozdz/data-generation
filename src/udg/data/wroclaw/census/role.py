from udg.data.generator import Generator
from udg.features.family import ChildNumber, FamilyType
from udg.features.person import Role
from udg.model.model import Family


def _has_no_role(role: Role, family: Family) -> bool:
    return not any(person.features[Role] is role for person in family.persons)


def _count_role(role: Role, family: Family) -> int:
    return sum(1 for person in family.persons if person.features[Role] is role)


class RoleSelector(Generator[Role]):
    def generate(
        self,
        family_type: FamilyType,
        family: Family,
        child_number: ChildNumber,
    ) -> Role:
        # Start with children so that the parents' age can be calculated appropriately.
        if _count_role(Role.CHILD, family) < child_number:
            return Role.CHILD

        if family_type is FamilyType.MOTHER_WITH_CHILDREN:
            if _has_no_role(Role.MOTHER, family):
                return Role.MOTHER
        elif family_type is FamilyType.FATHER_WITH_CHILDREN:
            if _has_no_role(Role.FATHER, family):
                return Role.FATHER
        elif family_type is not FamilyType.NONE:
            if _has_no_role(Role.MOTHER, family):
                return Role.MOTHER
            elif _has_no_role(Role.FATHER, family):
                return Role.FATHER

        return Role.OTHER

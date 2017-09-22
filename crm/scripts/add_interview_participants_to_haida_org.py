from crm.models import Person, Organization


def run(*args):
    o = Organization.objects.get(name='Haida Community')
    for p in Person.objects.filter(roles__name__contains="Interview Participant"):
        o.person_set.add(p)
        print("Adding:", p)

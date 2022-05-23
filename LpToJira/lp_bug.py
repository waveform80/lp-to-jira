# Simple LaunchPad Bug object used to store some informations from LaunchPad
# into a structure that can be stored in and out of a json file

ubuntu_devel = 'Kinetic'

ubuntu_versions = {
    ubuntu_devel: '22.10',
    'Jammy': '22.04',
    'Impish': '21.10',
    'Hirsute': '21.04',
    'Groovy': '20.10',
    'Focal': '20.04',
    'Bionic': '18.04',
    'Xenial': '16.04',
    'Trusty': '14.04',
    'Precise': '12.04'
}


class lp_bug():
    def __init__(self, id, lp_api):
        self.id = int(id)

        if not lp_api:
            raise ValueError("Error with Launchpad API")

        try:
            bug = lp_api.bugs[self.id]

        except KeyError:
            raise KeyError("Bug {} isn't in Launchpad".format(id))

        self.title = bug.title
        self.description = bug.description
        self.heat = bug.heat

        self.packages_info = {}
        for task in bug.bug_tasks:
            package_name = ""

            task_name = task.bug_target_name
            if " (Ubuntu" in task_name:
                package_name = task_name.split()[0]

                if package_name not in self.packages_info:
                    self.packages_info[package_name] = {}

                # Grab the Ubuntu serie our of the task name
                # Set the serie to ubuntu_devel is empty
                serie = task_name[task_name.index("Ubuntu")+7:-1]
                if serie == '':
                    serie = ubuntu_devel
                elif serie not in ubuntu_versions:
                    continue

                if "series" not in self.packages_info[package_name]:
                    self.packages_info[package_name]["series"] = {}

                if serie not in self.packages_info[package_name]["series"]:
                    self.packages_info[package_name]["series"][serie] = {}

                # For each impacted package/serie, capture status
                self.packages_info[package_name]["series"][serie]["status"]\
                    = task.status

                # For each impacted package/serie, capture importance
                self.packages_info[package_name]["series"][serie]["importance"]\
                    = task.importance

    @property
    def affected_packages(self):
        """
        return list of packages affected by this bug in a form of string list
        ['pkg1', 'pkg2' , 'pkg3']
        """
        return list(self.packages_info)

    def affected_series(self, package):
        """
        Returns a list of string containing the series affected by a specific
        bug for a specific package: ['Impish', 'Focal', 'Bionic']
        """
        if package in self.packages_info:
            return list(self.packages_info[package]['series'])
        return []

    def affected_versions(self, package):
        """
        Simply return all the affected version for a specific package affected
        by this bug. Convert affected serie into a version number
        """
        return [ubuntu_version.get(x) for x in self.affected_series(package)]

    def package_detail(self, package, serie, detail):
        try:
            return self.packages_info[package]["series"][serie][detail]
        except KeyError:
            return ""

    def __repr__(self):
        return str(self.dict())

    def __str__(self):
        lines = []
        lines.append("LP: #{self.id} : {self.title}".format(self=self))
        lines.append("Heat: {self.heat}".format(self=self))
        for pkg in self.affected_packages:
            lines.append(" - {pkg}:".format(pkg=pkg))
            for serie in self.affected_series(pkg):
                lines.append("   - {serie} : {status} ({importance})".format(
                    serie=serie,
                    status=self.package_detail(pkg, serie, "status"),
                    importance=self.package_detail(pkg, serie, "importance")))
        return '\n'.join(lines)

    def dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'packages': self.packages_info,
        }

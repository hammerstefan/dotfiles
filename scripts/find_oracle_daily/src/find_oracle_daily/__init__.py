"""find_oracle_daily: resolve an Ubuntu daily image on Oracle Cloud to one OCID.

Example, substituting the result directly into a launch command::

    IMG=$(find-oracle-daily resolute) || exit 1
    oci compute instance launch --image-id "$IMG" ...
"""

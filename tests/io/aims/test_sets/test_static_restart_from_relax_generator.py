"""The test of input sets generating from restart information"""
from __future__ import annotations

import gzip
import json
import os
import shutil
from glob import glob
from pathlib import Path

from pymatgen.core import Lattice, Molecule, Structure
from pymatgen.io.aims.sets.core import StaticSetGenerator


def compare_files(test_name, work_dir, ref_dir):
    for file in glob(f"{work_dir / test_name}/*in"):
        with open(file) as test_file:
            test_lines = [line.strip() for line in test_file.readlines()[4:] if len(line.strip()) > 0]

        with gzip.open(f"{ref_dir / test_name / Path(file).name}.gz", "rt") as ref_file:
            ref_lines = [line.strip() for line in ref_file.readlines()[4:] if len(line.strip()) > 0]

        assert test_lines == ref_lines

    with open(f"{ref_dir / test_name}/parameters.json") as ref_file:
        ref = json.load(ref_file)
    ref.pop("species_dir", None)

    with open(f"{work_dir / test_name}/parameters.json") as check_file:
        check = json.load(check_file)
    check.pop("species_dir", None)

    assert ref == check


def comp_system(atoms, prev_dir, test_name, work_path, ref_path, species_dir):
    generator = StaticSetGenerator(user_parameters={})
    # adjust species dir in the prev_dir
    params_file = Path(prev_dir) / "parameters.json"
    shutil.copy(params_file, Path(prev_dir) / "~parameters.json")
    with open(params_file) as f:
        params = json.load(f)
    params["species_dir"] = (species_dir / "light").as_posix()
    with open(params_file, "w") as f:
        json.dump(params, f)

    input_set = generator.get_input_set(atoms, prev_dir, properties=["energy", "forces", "stress"])
    input_set.write_input(work_path / test_name)
    compare_files(test_name, work_path, ref_path)
    shutil.move(Path(prev_dir) / "~parameters.json", params_file)


O2 = Molecule(species=["O", "O"], coords=[[0, 0, 0.622978], [0, 0, -0.622978]])

Si = Structure(
    lattice=Lattice([[0.0, 2.715, 2.715], [2.715, 0.0, 2.715], [2.715, 2.715, 0.0]]),
    species=["Si", "Si"],
    coords=[[0, 0, 0], [0.25, 0.25, 0.25]],
)
species_dir = Path(__file__).resolve().parents[1] / "species_directory"

module_dir = Path(__file__).resolve().parents[1]
ref_path = (module_dir / "aims_input_generator_ref").resolve()


def test_static_from_relax_si(tmp_path):
    comp_system(
        Si,
        f"{ref_path}/relax-si/outputs",
        "static-from-prev-si",
        tmp_path,
        ref_path,
        species_dir,
    )


def test_static_from_relax_si_no_kgrid(tmp_path):
    comp_system(
        Si,
        f"{ref_path}/relax-no-kgrid-si/",
        "static-from-prev-no-kgrid-si",
        tmp_path,
        ref_path,
        species_dir,
    )


def test_static_from_relax_default_species_dir(tmp_path):
    sd_def = os.getenv("AIMS_SPECIES_DIR", None)
    os.environ["AIMS_SPECIES_DIR"] = str(species_dir / "light")

    comp_system(
        Si,
        f"{ref_path}/relax-default-sd-si/",
        "static-from-prev-default-sd-si",
        tmp_path,
        ref_path,
        species_dir,
    )

    if sd_def:
        os.environ["AIMS_SPECIES_DIR"] = sd_def
    else:
        os.unsetenv("AIMS_SPECIES_DIR")


def test_static_from_relax_o2(tmp_path):
    comp_system(
        O2,
        f"{ref_path}/relax-o2/",
        "static-from-prev-o2",
        tmp_path,
        ref_path,
        species_dir,
    )


def test_static_from_relax_default_species_dir_o2(tmp_path):
    sd_def = os.getenv("AIMS_SPECIES_DIR", None)
    os.environ["AIMS_SPECIES_DIR"] = str(species_dir / "light")

    comp_system(
        O2,
        f"{ref_path}/relax-default-sd-o2/",
        "static-from-prev-default-sd-o2",
        tmp_path,
        ref_path,
        species_dir,
    )

    if sd_def:
        os.environ["AIMS_SPECIES_DIR"] = sd_def
    else:
        os.unsetenv("AIMS_SPECIES_DIR")
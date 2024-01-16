import pyaedt
from pyaedt.modeler.pcb import object3dlayout
import matplotlib.pyplot as pyplot

# import mcm

Design = pyaedt.Edb(edbpath='./example/Mutant.mcm')

# cutout
signal_list = []
for net in Design.nets.netlist:
    if ("HTX" in net) or ("HRX" in net):
        signal_list.append(net)

GND_list = ["VSS"]

Design.cutout(signal_list=signal_list,
              reference_list=GND_list, extent_type="Bounding")

# adjust stackup only for UBM

Design.stackup.remove_layer(name="UBM_Z1-DIE1")
Design.stackup.load("./example/Final_stackup.xml")
Design.save_edb()

# open 3dlayout

h3d = pyaedt.Hfss3dLayout(projectname="./example/Mutant.aedb",
                          specified_version="2023.1", new_desktop_session=True, non_graphical=False)

# set bump/ball
primitives = h3d.modeler
bga = object3dlayout.Components3DLayout(primitives=primitives, name="BGA")
die = object3dlayout.Components3DLayout(primitives=primitives, name="DIE")

bga.set_property_value(property_name="Part Type", property_value="IC")
die.set_property_value(property_name="Part Type", property_value="IC")

bga.set_die_type(die_type=1, orientation=0)
die.set_die_type(die_type=1, orientation=1)

bga.set_solderball(solderball_type='Cy1', diameter='0.3mm',
                   mid_diameter='0.3mm', height='0.2mm', material='solder')
die.set_solderball(solderball_type='Cy1', diameter='0.08mm',
                   mid_diameter='0.08mm', height='0.06mm', material='solder')

# create ports
h3d.create_ports_on_component_by_nets('BGA', signal_list)
h3d.create_ports_on_component_by_nets('DIE', signal_list)

# set boundary
h3d.edit_hfss_extents(diel_extent_horizontal_padding='0.2mm', air_vertical_negative_padding='3mm',
                      air_vertical_positive_padding='3mm', air_horizontal_padding='3mm')

# set mesh method
h3d.set_meshing_settings(mesh_method="PhiPlus")

# create setup
Mysetup = h3d.create_setup(setupname="Setup1")
Mysetup.props["AdaptiveSettings"]["AdaptType"] = "kMultiFrequencies"
Mysetup.props["AdaptiveSettings"]["MultiFrequencyDataList"]["AdaptiveFrequencyData"][0]["AdaptiveFrequency"] = "1GHz"
Mysetup.props["AdaptiveSettings"]["MultiFrequencyDataList"]["AdaptiveFrequencyData"][1]["AdaptiveFrequency"] = "28GHz"
Mysetup.props["AdaptiveSettings"]["MultiFrequencyDataList"]["AdaptiveFrequencyData"][2]["AdaptiveFrequency"] = "50GHz"

Mysetup.props["AdaptiveSettings"]["SingleFrequencyDataList"]["AdaptiveFrequencyData"]["MaxPasses"] = 20

Mysetup.props["AdaptiveSettings"]["BroadbandFrequencyDataList"]["AdaptiveFrequencyData"][0]["MaxPasses"] = 20
Mysetup.props["AdaptiveSettings"]["BroadbandFrequencyDataList"]["AdaptiveFrequencyData"][1]["MaxPasses"] = 20

Mysetup.props["AdaptiveSettings"]["MultiFrequencyDataList"]["AdaptiveFrequencyData"][0]["MaxPasses"] = 20
Mysetup.props["AdaptiveSettings"]["MultiFrequencyDataList"]["AdaptiveFrequencyData"][1]["MaxPasses"] = 20
Mysetup.props["AdaptiveSettings"]["MultiFrequencyDataList"]["AdaptiveFrequencyData"][2]["MaxPasses"] = 20

Mysetup.props["ViaNumSides"] = 12
Mysetup.props["CurveApproximation"]["ArcAngle"] = "30deg"
Mysetup.props["CurveApproximation"]["MaxPoints"] = 8
Mysetup.update()
MySweep = h3d.create_linear_step_sweep(setupname=Mysetup.name, sweepname="Sweep1", unit="GHz", freqstart=0, freqstop=50,
                                       step_size=0.05, sweep_type="Interpolating", interpolation_tol_percent=0.1, interpolation_max_solutions=1000)
h3d.save_project()

# analyze
h3d.analysis_setup(Mysetup.name, num_cores=64, num_tasks=1)
h3d.export_touchstone(setup_name=Mysetup.name, sweep_name="Sweep1")
# release APP
h3d.release_desktop()

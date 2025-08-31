import json
import os.path
import time

from blockchain import Blockchain, generate_private_key, generate_public_key, Block
from utils import b64


def link_descendants(proportion: float, name: str, travel_distance: float, blockchain_index: int = None) -> list[float,
dict]:
    return [proportion, {'name': name,
                         'travel_distance': travel_distance,
                         'blockchain_index': blockchain_index}]


def generate_stage_json(name: str, country: str, city: str, batch_size: float, batch_size_units: str, factory_name: str,
                        descendants: list[list[float, dict[float, dict]]],
                        notes: str = None):
    data = {
        'name': name,
        'city': city,
        'country': country,
        'batch_size': batch_size,
        'batch_size_units': batch_size_units,
        'components': descendants,
        'factory_name': factory_name,
        'notes': notes
    }
    return data


BLOCKCHAIN_PATH = 'populated.blockchain'

if os.path.exists(BLOCKCHAIN_PATH):
    os.remove(BLOCKCHAIN_PATH)
blockchain = Blockchain.load(BLOCKCHAIN_PATH, create=True)


def add_block_random_origin(data: dict):
    # Random origin = Private keys are being discarded who cares its for testing
    private_key = generate_private_key()
    public_key = generate_public_key(private_key)
    data_bytes = json.dumps(data).encode()
    block = Block(data_bytes, blockchain.last_index + 1, blockchain.last_hash, public_key, time.time())
    block.sign(private_key)
    blockchain.add_block(block.serialize())
    return block


hide_block = add_block_random_origin(generate_stage_json(
    'Crocodile Hide',
    'Vietnam', 'Ho Chi Minh', 30, 'pieces',
    'Croco Farming Ltd', [], 'Known for excessive animal cruelty',
))

string_block = add_block_random_origin(generate_stage_json(
    'String Rolls',
    'China', 'Beijing', 30, 'kg',
    'Rolling Dragon Ltd', [], 'No known issues with the company',
))

leather_block = add_block_random_origin(generate_stage_json(
    'Leather Sheets Assembly',
    'China', 'Beijing', 60, 'pieces',
    'Leather Weather Factory', [link_descendants(0.9, 'Crocodile Hide', 2300, hide_block.index),
                                (link_descendants(0.1, 'String Rolls', 600, string_block.index))],
    'No known issues with the company',
))

buttons_block = add_block_random_origin(generate_stage_json(
    'Metal & Plastic Buttons',
    'Germany', 'Hamburg', 100, 'pieces',
    'ButtonTech GmbH', [], 'No known issues',
))

assembly_block = add_block_random_origin(generate_stage_json(
    'Luxury Bag Assembly',
    'France', 'Paris', 50, 'bags',
    'Haute Bags Ltd', [
        link_descendants(0.7, 'Leather Sheets Assembly', 7890, leather_block.index),
        link_descendants(0.2, 'String Rolls', 8000, string_block.index),
        link_descendants(0.1, 'Buttons/Hardware', 1230, buttons_block.index)
    ],
    'No known issues with the assembly company',
))

# Layer 1 (Raw Materials)
copper_block = add_block_random_origin(generate_stage_json(
    'Copper Ore',
    'Chile', 'Santiago', 500, 'tons',
    'Andes Mining Corp', [], 'Environmental concerns with mining runoff',
))

iron_block = add_block_random_origin(generate_stage_json(
    'Iron Ore',
    'Australia', 'Perth', 1000, 'tons',
    'DownUnder Mining Ltd', [], 'No known issues',
))

plastic_block = add_block_random_origin(generate_stage_json(
    'Petrochemical Plastic Pellets',
    'Saudi Arabia', 'Riyadh', 200, 'tons',
    'PetroPlastics Co.', [], 'Linked to oil-related carbon emissions',
))

silicon_block = add_block_random_origin(generate_stage_json(
    'Silicon Wafers',
    'Taiwan', 'Hsinchu', 300, 'kg',
    'Taiwan Silicon Works', [], 'No known issues',
))

# Cant be bothered making those myself, so those r AI (previous ones are my manual labour :( )
# START AI GENERATED CONTENT -=-=-=-=-=-=-=-=-=-=-=-=-=
copper_block = add_block_random_origin(generate_stage_json(
    'Copper Ore',
    'Chile', 'Antofagasta', 2000, 'tons',
    'Andes Mining Corp', [], 'Water-intensive mining operations',
))

neodymium_block = add_block_random_origin(generate_stage_json(
    'Neodymium Ore',
    'China', 'Baotou', 500, 'tons',
    'Baotou Rare Earths Ltd', [], 'Toxic waste issues',
))

graphite_block = add_block_random_origin(generate_stage_json(
    'Natural Graphite',
    'Mozambique', 'Montepuez', 800, 'tons',
    'MozGraph Co.', [], 'Local community disputes',
))

silicon_block = add_block_random_origin(generate_stage_json(
    'High-Purity Silicon',
    'USA', 'San Jose', 600, 'tons',
    'SilicaPure Inc', [], 'Energy-intensive production',
))

plastic_block = add_block_random_origin(generate_stage_json(
    'Polymer Resin Pellets',
    'Saudi Arabia', 'Jubail', 1000, 'tons',
    'PetroPlastics Ltd', [], 'Carbon emissions linked to oil refining',
))

steel_block = add_block_random_origin(generate_stage_json(
    'Alloy Steel',
    'India', 'Bhubaneswar', 3000, 'tons',
    'Bharat Alloys Ltd', [], 'No known issues',
))

# LAYER 2 (Refined / processed materials)
copper_wire_block = add_block_random_origin(generate_stage_json(
    'Ultra-Fine Copper Wire',
    'Vietnam', 'Hai Phong', 700, 'tons',
    'VietCopper Ltd',
    [
        # copper ore (Antofagasta -> Hai Phong): ~19,485 km
        link_descendants(1.0, 'Copper Ore', 19485, copper_block.index)
    ],
    'No known issues',
))

neodymium_ingots_block = add_block_random_origin(generate_stage_json(
    'Neodymium Ingots',
    'China', 'Shenzhen', 400, 'tons',
    'NeoMaterials Ltd',
    [
        # Baotou -> Shenzhen: ~2,049 km
        link_descendants(1.0, 'Neodymium Ore', 2049, neodymium_block.index)
    ],
    'Environmental risk from rare earth processing',
))

epoxy_block = add_block_random_origin(generate_stage_json(
    'Epoxy Resin',
    'Germany', 'Frankfurt', 500, 'tons',
    'ChemResin GmbH',
    [
        # Polymer resin (Jubail -> Frankfurt): ~4,309 km
        link_descendants(1.0, 'Polymer Resin Pellets', 4309, plastic_block.index)
    ],
    'No known issues',
))

semiconductor_block = add_block_random_origin(generate_stage_json(
    'Power Semiconductors',
    'Taiwan', 'Hsinchu', 300, 'kg',
    'Taiwan SemiWorks',
    [
        # Silicon (San Jose -> Hsinchu): ~10,484 km (Silicon sourced in San Jose -> fabs in Hsinchu)
        link_descendants(1.0, 'High-Purity Silicon', 10484, silicon_block.index)
    ],
    'No known issues',
))

bearing_steel_block = add_block_random_origin(generate_stage_json(
    'Hardened Bearing Steel',
    'Sweden', 'Lulea', 1200, 'tons',
    'NordicSteel AB',
    [
        # Alloy steel (Bhubaneswar -> Luleå): ~6,761 km
        link_descendants(1.0, 'Alloy Steel', 6761, steel_block.index)
    ],
    'No known issues',
))

# LAYER 3 (Motor Parts — distinct, non-repetitive)
stator_windings_block = add_block_random_origin(generate_stage_json(
    'Stator Windings (precision-wound)',
    'Japan', 'Nagoya', 1000, 'sets',
    'WindTech Co.',
    [
        # Copper wire (Hai Phong -> Nagoya): ~3,347 km
        link_descendants(0.8, 'Ultra-Fine Copper Wire', 3347, copper_wire_block.index),
        # Epoxy (Frankfurt -> Nagoya): ~9,255 km
        link_descendants(0.2, 'Epoxy Resin', 9255, epoxy_block.index)
    ],
    'High-precision winding process (automated tension control)',
))

rotor_magnets_block = add_block_random_origin(generate_stage_json(
    'Rotor Permanent Magnet Sets',
    'China', 'Guangzhou', 800, 'sets',
    'MagForce Ltd',
    [
        # Neodymium ingots (Shenzhen -> Guangzhou): ~98 km
        link_descendants(1.0, 'Neodymium Ingots', 98, neodymium_ingots_block.index)
    ],
    'Potential labor issues during ore processing',
))

bearing_block = add_block_random_origin(generate_stage_json(
    'Ceramic Ball Bearings (precision)',
    'Italy', 'Turin', 1500, 'units',
    'Ceramotion S.p.A.',
    [
        # Bearing steel (Luleå -> Turin): ~7,198 km
        link_descendants(0.7, 'Hardened Bearing Steel', 7198, bearing_steel_block.index),
        # Graphite (Montepuez -> Turin): ~7,198 km (Montepuez -> Turin actually ~7,198 km)
        # (we keep the split as raw graphite is processed near bearing factories)
        link_descendants(0.3, 'Natural Graphite', 7198, graphite_block.index)
    ],
    'Tight roundness and surface-finish tolerances',
))

pcb_block = add_block_random_origin(generate_stage_json(
    'Motor Driver PCB (bare board + SMD assembly)',
    'Vietnam', 'Da Nang', 1200, 'boards',
    'PCBWorks Ltd',
    [
        # Power semiconductors (Hsinchu -> Da Nang): ~1,644 km
        link_descendants(1.0, 'Power Semiconductors', 1644, semiconductor_block.index)
    ],
    'Solder reflow and conformal-coating ready',
))

housing_block = add_block_random_origin(generate_stage_json(
    'Aluminum Motor Housing (CNC & finish)',
    'Mexico', 'Guadalajara', 600, 'units',
    'AluCast SA',
    [
        # Alloy steel (Bhubaneswar -> Guadalajara): ~15,351 km (steel might be procured/processed globally)
        link_descendants(1.0, 'Alloy Steel', 15351, steel_block.index)
    ],
    'Precision CNC tolerances for housings',
))

# LAYER 4 (Sub-Assemblies)
rotor_block = add_block_random_origin(generate_stage_json(
    'BLDC Rotor Assembly (magnets fitted & balance-checked)',
    'South Korea', 'Incheon', 400, 'units',
    'K-Rotor Co.',
    [
        # Rotor magnets (Guangzhou -> Incheon): ~2,046 km
        link_descendants(0.7, 'Rotor Permanent Magnets', 2046, rotor_magnets_block.index),
        # Bearings (Turin -> Incheon): ~8,994 km
        link_descendants(0.3, 'Ceramic Ball Bearings', 8994, bearing_block.index),
    ],
    'Dynamic balancing for high RPMs',
))

stator_block = add_block_random_origin(generate_stage_json(
    'BLDC Stator Assembly',
    'Germany', 'Stuttgart', 500, 'units',
    'EuroStator GmbH',
    [
        # Stator windings (Nagoya -> Stuttgart): ~9,345 km
        link_descendants(1.0, 'Stator Windings', 9345, stator_windings_block.index)
    ],
    'Varnish cure & slot insulation applied',
))

controller_block = add_block_random_origin(generate_stage_json(
    'Electronic Speed Controller (ESC)',
    'Taiwan', 'Taipei', 700, 'units',
    'ESC Dynamics Ltd',
    [
        # PCB assemblies (Da Nang -> Taipei): ~1,706 km
        link_descendants(0.8, 'Motor Driver PCB', 1706, pcb_block.index),
        # Epoxy (Frankfurt -> Taipei): ~9,374 km (for potting/encapsulation or adhesives sometimes sourced globally)
        link_descendants(0.2, 'Epoxy Resin', 1706, epoxy_block.index)
    ],
    'Firmware flash & thermal profiling performed',
))

sensor_block = add_block_random_origin(generate_stage_json(
    'Hall Effect / Rotor Position Sensors (SMD + test)',
    'Singapore', 'Singapore', 1000, 'units',
    'Sensorix Pte Ltd',
    [
        # Semiconductors (Hsinchu -> Singapore): ~3,196 km
        link_descendants(1.0, 'Power Semiconductors', 3196, semiconductor_block.index)
    ],
    'High-reliability sensor calibration',
))

# LAYER 5 (Final BLDC Motor Assembly)
bldc_motor_block = add_block_random_origin(generate_stage_json(
    'Brushless DC Motor Assembly',
    'USA', 'Detroit', 300, 'motors',
    'MotorWorks Inc',
    [
        # Rotor (Incheon -> Detroit): ~10,645 km
        link_descendants(0.25, 'BLDC Rotor Assembly', 10645, rotor_block.index),
        # Stator (Stuttgart -> Detroit): ~6,762 km
        link_descendants(0.25, 'BLDC Stator Assembly', 6762, stator_block.index),
        # ESC (Taipei -> Detroit): ~12,109 km
        link_descendants(0.20, 'Electronic Speed Controller (ESC)', 12109, controller_block.index),
        # Sensors (Singapore -> Detroit): ~15,115 km
        link_descendants(0.15, 'Hall Effect Sensors', 15115, sensor_block.index),
        # Housing (Guadalajara -> Detroit): ~3,065 3065
        link_descendants(0.15, 'Aluminum Motor Housing', 600, housing_block.index),
    ],
    'Final BLDC motor for drones, e-bikes, robotics; final test & QC in Detroit',
))
# End AI Generated Content

blockchain.save(BLOCKCHAIN_PATH)

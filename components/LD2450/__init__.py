import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import uart, binary_sensor, number, sensor, button, switch
from esphome.components.uart import UARTComponent
from esphome.const import (
    CONF_ID,
    CONF_NAME,
    CONF_STEP,
    CONF_RESTORE_VALUE,
    CONF_INITIAL_VALUE,
    CONF_UNIT_OF_MEASUREMENT,
    UNIT_METER,
    UNIT_CENTIMETER,
    UNIT_DEGREES,
    DEVICE_CLASS_OCCUPANCY,
    DEVICE_CLASS_DISTANCE,
    DEVICE_CLASS_SPEED,
    DEVICE_CLASS_RESTART,
    STATE_CLASS_MEASUREMENT,
    ICON_RESTART_ALERT,
    ENTITY_CATEGORY_DIAGNOSTIC,
    ENTITY_CATEGORY_CONFIG,
)

AUTO_LOAD = ["binary_sensor", "number", "sensor", "button", "switch"]

DEPENDENCIES = ["uart"]

UART_ID = "uart_id"

CONF_USE_FAST_OFF = "fast_off_detection"
CONF_FLIP_X_AXIS = "flip_x_axis"
CONF_OCCUPANCY = "occupancy"
CONF_TARGET_COUNT = "target_count"
CONF_MAX_DISTANCE = "max_detection_distance"
CONF_MAX_DISTANCE_MARGIN = "max_distance_margin"
CONF_TARGETS = "targets"
CONF_TARGET = "target"
CONF_DEBUG = "debug"
CONF_X_SENSOR = "x_position"
CONF_Y_SENSOR = "y_position"
CONF_SPEED_SENSOR = "speed"
CONF_DISTANCE_SENSOR = "distance"
CONF_DISTANCE_RESOLUTION_SENSOR = "distance_resolution"
CONF_ANGLE_SENSOR = "angle"
CONF_ZONES = "zones"
CONF_ZONE = "zone"
CONF_MARGIN = "margin"
CONF_TARGET_TIMEOUT = "target_timeout"
CONF_POLYGON = "polygon"
CONF_POINT = "point"
CONF_X = "x"
CONF_Y = "y"
CONF_RESTART_BUTTON = "restart_button"
CONF_FACTORY_RESET_BUTTON = "factory_reset_button"
CONF_TRACKING_MODE_SWITCH = "tracking_mode_switch"
UNIT_METER_PER_SECOND = "m/s"
ICON_ANGLE_ACUTE = "mdi:angle-acute"
ICON_ACCOUNT_GROUP = "mdi:account-group"

ld2450_ns = cg.esphome_ns.namespace("ld2450")
LD2450 = ld2450_ns.class_("LD2450", cg.Component, uart.UARTDevice)
Target = ld2450_ns.class_("Target", cg.Component)
MaxDistanceNumber = ld2450_ns.class_("MaxDistanceNumber", cg.Component)
PollingSensor = ld2450_ns.class_("PollingSensor", cg.PollingComponent)
Zone = ld2450_ns.class_("Zone")
EmptyButton = ld2450_ns.class_("EmptyButton", button.Button, cg.Component)
TrackingModeSwitch = ld2450_ns.class_("TrackingModeSwitch", switch.Switch, cg.Component)

DISTANCE_SENSOR_SCHEMA = (
    sensor.sensor_schema(
        unit_of_measurement=UNIT_METER,
        accuracy_decimals=2,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=DEVICE_CLASS_DISTANCE,
    )
    .extend(cv.polling_component_schema("1s"))
    .extend(
        {
            cv.GenerateID(): cv.declare_id(PollingSensor),
            cv.Optional(CONF_UNIT_OF_MEASUREMENT, default=UNIT_METER): cv.All(
                cv.one_of(UNIT_METER, UNIT_CENTIMETER),
            ),
        }
    )
)

SPEED_SENSOR_SCHEMA = (
    sensor.sensor_schema(
        unit_of_measurement=UNIT_METER_PER_SECOND,
        accuracy_decimals=0,
        state_class=STATE_CLASS_MEASUREMENT,
        device_class=DEVICE_CLASS_SPEED,
    )
    .extend(cv.polling_component_schema("1s"))
    .extend(
        {
            cv.GenerateID(): cv.declare_id(PollingSensor),
            cv.Optional(
                CONF_UNIT_OF_MEASUREMENT, default=UNIT_METER_PER_SECOND
            ): cv.All(
                cv.one_of(UNIT_METER_PER_SECOND),
            ),
        }
    )
)

DEGREE_SENSOR_SCHEMA = (
    sensor.sensor_schema(
        unit_of_measurement=UNIT_DEGREES,
        accuracy_decimals=0,
        state_class=STATE_CLASS_MEASUREMENT,
        icon=ICON_ANGLE_ACUTE,
    )
    .extend(cv.polling_component_schema("1s"))
    .extend(
        {
            cv.GenerateID(): cv.declare_id(PollingSensor),
            cv.Optional(CONF_UNIT_OF_MEASUREMENT, default=UNIT_DEGREES): cv.All(
                cv.one_of(UNIT_DEGREES),
            ),
        }
    )
)

TARGET_SCHEMA = cv.Schema(
    {
        cv.Required(CONF_TARGET): cv.Schema(
            {
                cv.GenerateID(): cv.declare_id(Target),
                cv.Optional(CONF_NAME): cv.string_strict,
                cv.Optional(CONF_DEBUG, default=False): cv.boolean,
                cv.Optional(CONF_X_SENSOR): DISTANCE_SENSOR_SCHEMA.extend(
                    cv.Schema(
                        {cv.Optional(CONF_NAME, default="X Position"): cv.string_strict}
                    )
                ),
                cv.Optional(CONF_Y_SENSOR): DISTANCE_SENSOR_SCHEMA.extend(
                    cv.Schema(
                        {cv.Optional(CONF_NAME, default="Y Position"): cv.string_strict}
                    )
                ),
                cv.Optional(CONF_SPEED_SENSOR): SPEED_SENSOR_SCHEMA.extend(
                    cv.Schema(
                        {cv.Optional(CONF_NAME, default="Speed"): cv.string_strict}
                    )
                ),
                cv.Optional(
                    CONF_DISTANCE_RESOLUTION_SENSOR
                ): DISTANCE_SENSOR_SCHEMA.extend(
                    cv.Schema(
                        {
                            cv.Optional(
                                CONF_NAME, default="Distance Resolution"
                            ): cv.string_strict
                        }
                    )
                ),
                cv.Optional(CONF_ANGLE_SENSOR): DEGREE_SENSOR_SCHEMA.extend(
                    cv.Schema(
                        {cv.Optional(CONF_NAME, default="Angle"): cv.string_strict}
                    )
                ),
                cv.Optional(CONF_DISTANCE_SENSOR): DISTANCE_SENSOR_SCHEMA.extend(
                    cv.Schema(
                        {cv.Optional(CONF_NAME, default="Distance"): cv.string_strict}
                    )
                ),
            }
        ),
    }
)

POLYGON_SCHEMA = cv.Schema(
    {
        cv.Required(CONF_POINT): cv.Schema(
            {
                cv.Required(CONF_X): cv.All(cv.distance),
                cv.Required(CONF_Y): cv.All(cv.distance),
            }
        )
    }
)


def is_convex(points):
    """Determine if the polygon given by the list of points is convex."""
    last_cross_product = None
    len_ = len(points)
    for i in range(0, len_ + 1):
        dx_1 = points[(i + 1) % len_][0] - points[i % len_][0]
        dy_1 = points[(i + 1) % len_][1] - points[i % len_][1]
        dx_2 = points[(i + 2) % len_][0] - points[(i + 1) % len_][0]
        dy_2 = points[(i + 2) % len_][1] - points[(i + 1) % len_][1]
        cross_product = dx_1 * dy_2 - dy_1 * dx_2

        if last_cross_product is not None and (
            (cross_product > 0 and last_cross_product < 0)
            or (cross_product > 0 and last_cross_product < 0)
        ):
            return False
        last_cross_product = cross_product
    return True


def validate_polygon(config):
    """Assert that the provided polygon is convex."""

    points = []
    for point_config in config[CONF_POLYGON]:
        point_config = point_config[CONF_POINT]
        points.append((float(point_config[CONF_X]), float(point_config[CONF_Y])))

    if not is_convex(points):
        raise cv.Invalid("Polygon is not convex (and non-intersecting).")

    return config


ZONE_SCHEMA = cv.Schema(
    {
        cv.Required(CONF_ZONE): cv.All(
            {
                cv.GenerateID(): cv.declare_id(Zone),
                cv.Required(CONF_NAME): cv.string_strict,
                cv.Optional(CONF_MARGIN, default="25cm"): cv.All(
                    cv.distance, cv.Range(min=0.0, max=6.0)
                ),
                cv.Optional(
                    CONF_TARGET_TIMEOUT, default="5s"
                ): cv.positive_time_period_milliseconds,
                cv.Required(CONF_POLYGON): cv.All(
                    cv.ensure_list(POLYGON_SCHEMA), cv.Length(min=3)
                ),
                cv.Optional(CONF_OCCUPANCY): binary_sensor.binary_sensor_schema(
                    device_class=DEVICE_CLASS_OCCUPANCY,
                ).extend(
                    cv.Schema({cv.Optional(CONF_NAME, default=""): cv.string_strict})
                ),
                cv.Optional(CONF_TARGET_COUNT): sensor.sensor_schema(
                    accuracy_decimals=0,
                ).extend(
                    cv.Schema({cv.Optional(CONF_NAME, default=""): cv.string_strict})
                ),
            },
            validate_polygon,
        )
    }
)

CONFIG_SCHEMA = uart.UART_DEVICE_SCHEMA.extend(
    {
        cv.GenerateID(): cv.declare_id(LD2450),
        cv.Required(UART_ID): cv.use_id(UARTComponent),
        cv.Optional(CONF_NAME, default="LD2450"): cv.string_strict,
        cv.Optional(CONF_TARGETS): cv.All(
            cv.ensure_list(TARGET_SCHEMA),
            cv.Length(min=1, max=3),
        ),
        cv.Optional(CONF_ZONES): cv.All(
            cv.ensure_list(ZONE_SCHEMA),
            cv.Length(min=1),
        ),
        cv.Optional(CONF_FLIP_X_AXIS, default=False): cv.boolean,
        cv.Optional(CONF_USE_FAST_OFF, default=False): cv.boolean,
        cv.Optional(CONF_OCCUPANCY): binary_sensor.binary_sensor_schema(
            device_class=DEVICE_CLASS_OCCUPANCY
        ),
        cv.Optional(CONF_TARGET_COUNT): sensor.sensor_schema(
            accuracy_decimals=0,
        ),
        cv.Optional(CONF_MAX_DISTANCE_MARGIN, default="25cm"): cv.All(
            cv.distance, cv.Range(min=0.0, max=6.0)
        ),
        cv.Optional(CONF_RESTART_BUTTON): button.button_schema(
            EmptyButton,
            entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            device_class=DEVICE_CLASS_RESTART,
        ),
        cv.Optional(CONF_FACTORY_RESET_BUTTON): button.button_schema(
            EmptyButton,
            entity_category=ENTITY_CATEGORY_CONFIG,
            icon=ICON_RESTART_ALERT,
        ),
        cv.Optional(CONF_TRACKING_MODE_SWITCH): switch.switch_schema(
            TrackingModeSwitch,
            icon=ICON_ACCOUNT_GROUP,
            entity_category=ENTITY_CATEGORY_CONFIG,
        ),
        cv.Optional(CONF_MAX_DISTANCE): cv.Any(
            cv.All(cv.distance, cv.Range(min=0.0, max=6.0)),
            number.NUMBER_SCHEMA.extend(
                {
                    cv.GenerateID(): cv.declare_id(MaxDistanceNumber),
                    cv.Required(CONF_NAME): cv.string_strict,
                    cv.Optional(CONF_INITIAL_VALUE, default="6.0m"): cv.All(
                        cv.distance, cv.Range(min=0.0, max=6.0)
                    ),
                    cv.Optional(CONF_STEP, default="10cm"): cv.All(
                        cv.distance, cv.Range(min=0.0, max=6.0)
                    ),
                    cv.Optional(CONF_RESTORE_VALUE, default=True): cv.boolean,
                    cv.Optional(
                        CONF_UNIT_OF_MEASUREMENT, default=UNIT_METER
                    ): cv.one_of(UNIT_METER, lower="true"),
                }
            ).extend(cv.COMPONENT_SCHEMA),
        ),
    }
)


def to_code(config):
    """Code generation for the LD2450 component."""
    var = cg.new_Pvariable(config[CONF_ID])
    yield cg.register_component(var, config)
    yield uart.register_uart_device(var, config)

    cg.add(var.set_name(config[CONF_NAME]))
    cg.add(var.set_flip_x_axis(config[CONF_FLIP_X_AXIS]))
    cg.add(var.set_fast_off_detection(config[CONF_USE_FAST_OFF]))
    cg.add(var.set_max_distance_margin(config[CONF_MAX_DISTANCE_MARGIN]))

    # process target list
    if targets_config := config.get(CONF_TARGETS):
        # Register target on controller
        for index, target_config in enumerate(targets_config):
            target = yield target_to_code(target_config[CONF_TARGET], index)
            cg.add(var.register_target(target))

    # process zones list
    if zones_config := config.get(CONF_ZONES):
        # Register target on controller
        for zone_config in zones_config:
            zone = yield zone_to_code(zone_config[CONF_ZONE])
            cg.add(var.register_zone(zone))

    # Add binary occupancy sensor if present
    if occupancy_config := config.get(CONF_OCCUPANCY):
        occupancy_binary_sensor = yield binary_sensor.new_binary_sensor(
            occupancy_config
        )
        cg.add(var.set_occupancy_binary_sensor(occupancy_binary_sensor))

    # Add target count sensor sensor if present
    if target_count_config := config.get(CONF_TARGET_COUNT):
        target_count_sensor = yield sensor.new_sensor(target_count_config)
        cg.add(var.set_target_count_sensor(target_count_sensor))

    # Add max distance value
    if max_distance_config := config.get(CONF_MAX_DISTANCE):
        # Add number component
        if isinstance(max_distance_config, dict):
            max_distance_number = yield number.new_number(
                max_distance_config,
                min_value=0.0,
                max_value=6.0,
                step=max_distance_config[CONF_STEP],
            )
            yield cg.register_parented(max_distance_number, config[CONF_ID])
            yield cg.register_component(max_distance_number, max_distance_config)
            cg.add(
                max_distance_number.set_initial_state(
                    max_distance_config[CONF_INITIAL_VALUE]
                )
            )
            cg.add(
                max_distance_number.set_restore(max_distance_config[CONF_RESTORE_VALUE])
            )
            cg.add(var.set_max_distance_number(max_distance_number))
        elif isinstance(max_distance_config, float):
            # Set fixed value from simple config
            cg.add(var.set_max_distance(max_distance_config))

    # Add sensor restart button if present
    if restart_config := config.get(CONF_RESTART_BUTTON):
        restart_button = yield button.new_button(restart_config)
        cg.add(var.set_restart_button(restart_button))

    # Add sensor factory reset button if present
    if reset_config := config.get(CONF_FACTORY_RESET_BUTTON):
        reset_button = yield button.new_button(reset_config)
        cg.add(var.set_factory_reset_button(reset_button))

    # Add tracking mode switch
    if tracking_mode_config := config.get(CONF_TRACKING_MODE_SWITCH):
        mode_switch = cg.new_Pvariable(tracking_mode_config[CONF_ID])
        yield cg.register_parented(mode_switch, config[CONF_ID])
        yield cg.register_component(mode_switch, tracking_mode_config)
        yield switch.register_switch(mode_switch, tracking_mode_config)
        cg.add(var.set_tracking_mode_switch(mode_switch))


def target_to_code(config, user_index: int):
    """Code generation for targets within the target list."""
    target = cg.new_Pvariable(config[CONF_ID])
    yield cg.register_component(target, config)

    # Generate name if not provided
    if CONF_NAME not in config:
        config[CONF_NAME] = f"Target {user_index + 1}"
    cg.add(target.set_name(config[CONF_NAME]))
    cg.add(target.set_debugging(config[CONF_DEBUG]))

    for SENSOR in [
        CONF_X_SENSOR,
        CONF_Y_SENSOR,
        CONF_SPEED_SENSOR,
        CONF_DISTANCE_RESOLUTION_SENSOR,
        CONF_ANGLE_SENSOR,
        CONF_DISTANCE_SENSOR,
    ]:
        if sensor_config := config.get(SENSOR):
            # Add Target name as prefix to sensor name
            sensor_config[CONF_NAME] = (
                f"{config[CONF_NAME]} {sensor_config[CONF_NAME]}"
                if CONF_NAME in sensor_config
                else config[CONF_NAME]
            )

            sensor_var = cg.new_Pvariable(sensor_config[CONF_ID])
            yield cg.register_component(sensor_var, sensor_config)
            yield sensor.register_sensor(sensor_var, sensor_config)

            if SENSOR == CONF_X_SENSOR:
                cg.add(target.set_x_position_sensor(sensor_var))
            elif SENSOR == CONF_Y_SENSOR:
                cg.add(target.set_y_position_sensor(sensor_var))
            elif SENSOR == CONF_SPEED_SENSOR:
                cg.add(target.set_speed_sensor(sensor_var))
            elif SENSOR == CONF_DISTANCE_RESOLUTION_SENSOR:
                cg.add(target.set_distance_resolution_sensor(sensor_var))
            elif SENSOR == CONF_ANGLE_SENSOR:
                cg.add(target.set_angle_sensor(sensor_var))
            elif SENSOR == CONF_DISTANCE_SENSOR:
                cg.add(target.set_distance_sensor(sensor_var))

    return target


def zone_to_code(config):
    """Code generation for zones and their sub-sensors."""
    zone = cg.new_Pvariable(config[CONF_ID])

    cg.add(zone.set_name(config[CONF_NAME]))
    cg.add(zone.set_margin(config[CONF_MARGIN]))
    cg.add(zone.set_target_timeout(config[CONF_TARGET_TIMEOUT]))

    # Add points to the polygon of the zone object
    for point_config in config[CONF_POLYGON]:
        point_config = point_config[CONF_POINT]

        cg.add(
            zone.append_point(
                (float(point_config[CONF_X])), float(point_config[CONF_Y])
            )
        )

    # Add binary occupancy sensor if present
    if occupancy_config := config.get(CONF_OCCUPANCY):
        occupancy_config[CONF_NAME] = (
            f"{config[CONF_NAME]} {occupancy_config[CONF_NAME]}"
            if occupancy_config.get(CONF_NAME, "") != ""
            else config[CONF_NAME]
        )
        occupancy_binary_sensor = yield binary_sensor.new_binary_sensor(
            occupancy_config
        )
        cg.add(zone.set_occupancy_binary_sensor(occupancy_binary_sensor))

    # Add target count sensor sensor if present
    if target_count_config := config.get(CONF_TARGET_COUNT):
        target_count_config[CONF_NAME] = (
            f"{config[CONF_NAME]} {target_count_config[CONF_NAME]}"
            if target_count_config.get(CONF_NAME, "") != ""
            else config[CONF_NAME]
        )
        target_count_sensor = yield sensor.new_sensor(target_count_config)
        cg.add(zone.set_target_count_sensor(target_count_sensor))

    return zone

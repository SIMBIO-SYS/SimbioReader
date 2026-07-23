from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lxml.etree import _Element


@dataclass(slots=True, frozen=True)
class BodyIdentification:
    body_spice_name: str
    name: str


@dataclass(slots=True, frozen=True)
class ReferenceFrame:
    frame_spice_name: str
    name: str


@dataclass(slots=True, frozen=True)
class GeometryDisplay:
    local_identifier_reference: str
    local_reference_type: str
    horizontal_display_axis: str
    horizontal_display_direction: str
    vertical_display_axis: str
    vertical_display_direction: str
    central_body: BodyIdentification
    target: BodyIdentification
    right_ascension_angle: float
    right_ascension_angle_unit: str
    declination_angle: float
    declination_angle_unit: str
    celestial_north_clock_angle: float
    celestial_north_clock_angle_unit: str
    reference_frame: ReferenceFrame


@dataclass(slots=True, frozen=True)
class CoordinateSystem:
    coordinate_system_type: str
    origin: BodyIdentification
    reference_frame: ReferenceFrame


@dataclass(slots=True, frozen=True)
class OrbiterIdentification:
    central_body: BodyIdentification
    target: BodyIdentification
    coordinate_system: CoordinateSystem


@dataclass(slots=True, frozen=True)
class PixelDimensions:
    field_of_view_method: str
    reference_location: str
    horizontal_pixel_footprint: float
    horizontal_pixel_footprint_unit: str
    vertical_pixel_footprint: float
    vertical_pixel_footprint_unit: str


@dataclass(slots=True, frozen=True)
class GeometryDistances:
    target_heliocentric_distance: float
    target_heliocentric_distance_unit: str
    spacecraft_target_center_distance: float
    spacecraft_target_center_distance_unit: str
    spacecraft_target_boresight_intercept_distance: float
    spacecraft_target_boresight_intercept_distance_unit: str


@dataclass(slots=True, frozen=True)
class PixelIntercept:
    reference_pixel_location: str
    vertical_coordinate_pixel: int
    vertical_coordinate_pixel_unit: str
    horizontal_coordinate_pixel: int
    horizontal_coordinate_pixel_unit: str
    latitude: float
    latitude_unit: str
    longitude: float
    longitude_unit: str


@dataclass(slots=True, frozen=True)
class SurfaceGeometry:
    footprint_vertices: tuple[PixelIntercept, ...]
    subsolar_latitude: float
    subsolar_latitude_unit: str
    subsolar_longitude: float
    subsolar_longitude_unit: str
    subspacecraft_latitude: float
    subspacecraft_latitude_unit: str
    subspacecraft_longitude: float
    subspacecraft_longitude_unit: str


@dataclass(slots=True, frozen=True)
class IlluminationGeometry:
    minimum_emission_angle: float
    minimum_emission_angle_unit: str
    maximum_emission_angle: float
    maximum_emission_angle_unit: str
    minimum_incidence_angle: float
    minimum_incidence_angle_unit: str
    maximum_incidence_angle: float
    maximum_incidence_angle_unit: str
    minimum_phase_angle: float
    minimum_phase_angle_unit: str
    maximum_phase_angle: float
    maximum_phase_angle_unit: str


@dataclass(slots=True, frozen=True)
class CartesianPositionVector:
    x: float
    x_unit: str
    y: float
    y_unit: str
    z: float
    z_unit: str
    light_time_correction_applied: str


@dataclass(slots=True, frozen=True)
class CartesianVelocityVector:
    x: float
    x_unit: str
    y: float
    y_unit: str
    z: float
    z_unit: str
    light_time_correction_applied: str


@dataclass(slots=True, frozen=True)
class GeometryVectors:
    earth_to_spacecraft: CartesianPositionVector | None = None
    spacecraft_to_target: CartesianPositionVector | None = None
    sun_to_spacecraft: CartesianPositionVector | None = None
    sun_to_target: CartesianPositionVector | None = None
    spacecraft_relative_to_earth: CartesianVelocityVector | None = None
    spacecraft_relative_to_sun: CartesianVelocityVector | None = None
    spacecraft_relative_to_target: CartesianVelocityVector | None = None


@dataclass(slots=True, frozen=True)
class GeometryOrbiter:
    reference_time_utc: datetime
    identification: OrbiterIdentification
    pixel_dimensions: PixelDimensions
    distances: GeometryDistances
    surface: SurfaceGeometry
    illumination: IlluminationGeometry
    vectors: GeometryVectors


@dataclass(slots=True, frozen=True)
class Geometry:
    kernel_type: str
    spice_kernel_file_name: str
    image_display: GeometryDisplay
    orbiter: GeometryOrbiter

    @classmethod
    def from_xml(
        cls,
        element: _Element,
        namespaces: dict[str, str],
    ) -> Geometry:
        """Build geometry metadata from the PDS discipline-area XML."""

        def text(path: str, context: _Element = element) -> str:
            value = str(
                context.xpath(f"string({path})", namespaces=namespaces)
            ).strip()
            if not value:
                raise ValueError(f"Missing geometry XML value at {path}")
            return value

        def unit(path: str, context: _Element = element) -> str:
            return text(f"{path}/@unit", context)

        def body(path: str, context: _Element = element) -> BodyIdentification:
            return BodyIdentification(
                body_spice_name=text(
                    f"{path}/geom:body_spice_name[1]", context
                ),
                name=text(f"{path}/geom:name[1]", context),
            )

        def frame(path: str, context: _Element = element) -> ReferenceFrame:
            return ReferenceFrame(
                frame_spice_name=text(
                    f"{path}/geom:frame_spice_name[1]", context
                ),
                name=text(f"{path}/geom:name[1]", context),
            )

        display_path = "geom:Image_Display_Geometry[1]"
        display_direction = f"{display_path}/geom:Display_Direction[1]"
        orientation = f"{display_path}/geom:Object_Orientation_RA_Dec[1]"
        orbiter_path = "geom:Geometry_Orbiter[1]"
        identification_path = (
            f"{orbiter_path}/geom:Orbiter_Identification[1]"
        )
        coordinate_path = (
            f"{identification_path}/geom:Coordinate_System_Identification[1]"
        )
        pixel_path = f"{orbiter_path}/geom:Pixel_Dimensions[1]"
        projected_path = f"{pixel_path}/geom:Pixel_Size_Projected[1]"
        distances_path = (
            f"{orbiter_path}/geom:Distances[1]/geom:Distances_Specific[1]"
        )
        surface_path = (
            f"{orbiter_path}/geom:Surface_Geometry[1]/"
            "geom:Surface_Geometry_Specific[1]"
        )
        illumination_path = (
            f"{orbiter_path}/geom:Illumination_Geometry[1]/"
            "geom:Illumination_Min_Max[1]"
        )
        intercepts = element.xpath(
            f"{surface_path}/geom:Footprint_Vertices[1]/"
            "geom:Pixel_Intercept",
            namespaces=namespaces,
        )

        image_display = GeometryDisplay(
            local_identifier_reference=text(
                f"{display_path}/pds:Local_Internal_Reference[1]/"
                "pds:local_identifier_reference[1]"
            ),
            local_reference_type=text(
                f"{display_path}/pds:Local_Internal_Reference[1]/"
                "pds:local_reference_type[1]"
            ),
            horizontal_display_axis=text(
                f"{display_direction}/geom:horizontal_display_axis[1]"
            ),
            horizontal_display_direction=text(
                f"{display_direction}/geom:horizontal_display_direction[1]"
            ),
            vertical_display_axis=text(
                f"{display_direction}/geom:vertical_display_axis[1]"
            ),
            vertical_display_direction=text(
                f"{display_direction}/geom:vertical_display_direction[1]"
            ),
            central_body=body(
                f"{display_path}/geom:Central_Body_Identification[1]"
            ),
            target=body(
                f"{display_path}/geom:Geometry_Target_Identification[1]"
            ),
            right_ascension_angle=float(
                text(f"{orientation}/geom:right_ascension_angle[1]")
            ),
            right_ascension_angle_unit=unit(
                f"{orientation}/geom:right_ascension_angle[1]"
            ),
            declination_angle=float(
                text(f"{orientation}/geom:declination_angle[1]")
            ),
            declination_angle_unit=unit(
                f"{orientation}/geom:declination_angle[1]"
            ),
            celestial_north_clock_angle=float(
                text(
                    f"{orientation}/geom:celestial_north_clock_angle[1]"
                )
            ),
            celestial_north_clock_angle_unit=unit(
                f"{orientation}/geom:celestial_north_clock_angle[1]"
            ),
            reference_frame=frame(
                f"{orientation}/geom:Reference_Frame_Identification[1]"
            ),
        )
        coordinate_system = CoordinateSystem(
            coordinate_system_type=text(
                f"{coordinate_path}/geom:coordinate_system_type[1]"
            ),
            origin=body(
                f"{coordinate_path}/"
                "geom:Coordinate_System_Origin_Identification[1]"
            ),
            reference_frame=frame(
                f"{coordinate_path}/geom:Reference_Frame_Identification[1]"
            ),
        )
        identification = OrbiterIdentification(
            central_body=body(
                f"{identification_path}/"
                "geom:Central_Body_Identification[1]"
            ),
            target=body(
                f"{identification_path}/"
                "geom:Geometry_Target_Identification[1]"
            ),
            coordinate_system=coordinate_system,
        )
        pixel_dimensions = PixelDimensions(
            field_of_view_method=text(
                f"{pixel_path}/geom:pixel_field_of_view_method[1]"
            ),
            reference_location=text(
                f"{projected_path}/geom:reference_location[1]"
            ),
            horizontal_pixel_footprint=float(
                text(
                    f"{projected_path}/"
                    "geom:horizontal_pixel_footprint[1]"
                )
            ),
            horizontal_pixel_footprint_unit=unit(
                f"{projected_path}/geom:horizontal_pixel_footprint[1]"
            ),
            vertical_pixel_footprint=float(
                text(
                    f"{projected_path}/geom:vertical_pixel_footprint[1]"
                )
            ),
            vertical_pixel_footprint_unit=unit(
                f"{projected_path}/geom:vertical_pixel_footprint[1]"
            ),
        )
        distances = GeometryDistances(
            target_heliocentric_distance=float(
                text(
                    f"{distances_path}/"
                    "geom:target_heliocentric_distance[1]"
                )
            ),
            target_heliocentric_distance_unit=unit(
                f"{distances_path}/geom:target_heliocentric_distance[1]"
            ),
            spacecraft_target_center_distance=float(
                text(
                    f"{distances_path}/"
                    "geom:spacecraft_target_center_distance[1]"
                )
            ),
            spacecraft_target_center_distance_unit=unit(
                f"{distances_path}/"
                "geom:spacecraft_target_center_distance[1]"
            ),
            spacecraft_target_boresight_intercept_distance=float(
                text(
                    f"{distances_path}/"
                    "geom:spacecraft_target_boresight_intercept_distance[1]"
                )
            ),
            spacecraft_target_boresight_intercept_distance_unit=unit(
                f"{distances_path}/"
                "geom:spacecraft_target_boresight_intercept_distance[1]"
            ),
        )
        surface = SurfaceGeometry(
            footprint_vertices=tuple(
                PixelIntercept(
                    reference_pixel_location=text(
                        "geom:reference_pixel_location[1]", item
                    ),
                    vertical_coordinate_pixel=int(
                        text(
                            "geom:Reference_Pixel[1]/"
                            "geom:vertical_coordinate_pixel[1]",
                            item,
                        )
                    ),
                    vertical_coordinate_pixel_unit=unit(
                        "geom:Reference_Pixel[1]/"
                        "geom:vertical_coordinate_pixel[1]",
                        item,
                    ),
                    horizontal_coordinate_pixel=int(
                        text(
                            "geom:Reference_Pixel[1]/"
                            "geom:horizontal_coordinate_pixel[1]",
                            item,
                        )
                    ),
                    horizontal_coordinate_pixel_unit=unit(
                        "geom:Reference_Pixel[1]/"
                        "geom:horizontal_coordinate_pixel[1]",
                        item,
                    ),
                    latitude=float(text("geom:pixel_latitude[1]", item)),
                    latitude_unit=unit("geom:pixel_latitude[1]", item),
                    longitude=float(text("geom:pixel_longitude[1]", item)),
                    longitude_unit=unit("geom:pixel_longitude[1]", item),
                )
                for item in intercepts
            ),
            subsolar_latitude=float(
                text(f"{surface_path}/geom:subsolar_latitude[1]")
            ),
            subsolar_latitude_unit=unit(
                f"{surface_path}/geom:subsolar_latitude[1]"
            ),
            subsolar_longitude=float(
                text(f"{surface_path}/geom:subsolar_longitude[1]")
            ),
            subsolar_longitude_unit=unit(
                f"{surface_path}/geom:subsolar_longitude[1]"
            ),
            subspacecraft_latitude=float(
                text(f"{surface_path}/geom:subspacecraft_latitude[1]")
            ),
            subspacecraft_latitude_unit=unit(
                f"{surface_path}/geom:subspacecraft_latitude[1]"
            ),
            subspacecraft_longitude=float(
                text(f"{surface_path}/geom:subspacecraft_longitude[1]")
            ),
            subspacecraft_longitude_unit=unit(
                f"{surface_path}/geom:subspacecraft_longitude[1]"
            ),
        )
        illumination = IlluminationGeometry(
            minimum_emission_angle=float(
                text(
                    f"{illumination_path}/geom:minimum_emission_angle[1]"
                )
            ),
            minimum_emission_angle_unit=unit(
                f"{illumination_path}/geom:minimum_emission_angle[1]"
            ),
            maximum_emission_angle=float(
                text(
                    f"{illumination_path}/geom:maximum_emission_angle[1]"
                )
            ),
            maximum_emission_angle_unit=unit(
                f"{illumination_path}/geom:maximum_emission_angle[1]"
            ),
            minimum_incidence_angle=float(
                text(
                    f"{illumination_path}/geom:minimum_incidence_angle[1]"
                )
            ),
            minimum_incidence_angle_unit=unit(
                f"{illumination_path}/geom:minimum_incidence_angle[1]"
            ),
            maximum_incidence_angle=float(
                text(
                    f"{illumination_path}/geom:maximum_incidence_angle[1]"
                )
            ),
            maximum_incidence_angle_unit=unit(
                f"{illumination_path}/geom:maximum_incidence_angle[1]"
            ),
            minimum_phase_angle=float(
                text(f"{illumination_path}/geom:minimum_phase_angle[1]")
            ),
            minimum_phase_angle_unit=unit(
                f"{illumination_path}/geom:minimum_phase_angle[1]"
            ),
            maximum_phase_angle=float(
                text(f"{illumination_path}/geom:maximum_phase_angle[1]")
            ),
            maximum_phase_angle_unit=unit(
                f"{illumination_path}/geom:maximum_phase_angle[1]"
            ),
        )
        vectors_path = (
            f"{orbiter_path}/geom:Vectors[1]/"
            "geom:Vectors_Cartesian_Specific[1]"
        )

        def position_vector(name: str) -> CartesianPositionVector | None:
            path = f"{vectors_path}/geom:{name}[1]"
            items = element.xpath(path, namespaces=namespaces)
            if not items:
                return None
            item = items[0]
            return CartesianPositionVector(
                x=float(text("geom:x_position[1]", item)),
                x_unit=unit("geom:x_position[1]", item),
                y=float(text("geom:y_position[1]", item)),
                y_unit=unit("geom:y_position[1]", item),
                z=float(text("geom:z_position[1]", item)),
                z_unit=unit("geom:z_position[1]", item),
                light_time_correction_applied=text(
                    "geom:light_time_correction_applied[1]",
                    item,
                ),
            )

        def velocity_vector(name: str) -> CartesianVelocityVector | None:
            path = f"{vectors_path}/geom:{name}[1]"
            items = element.xpath(path, namespaces=namespaces)
            if not items:
                return None
            item = items[0]
            return CartesianVelocityVector(
                x=float(text("geom:x_velocity[1]", item)),
                x_unit=unit("geom:x_velocity[1]", item),
                y=float(text("geom:y_velocity[1]", item)),
                y_unit=unit("geom:y_velocity[1]", item),
                z=float(text("geom:z_velocity[1]", item)),
                z_unit=unit("geom:z_velocity[1]", item),
                light_time_correction_applied=text(
                    "geom:light_time_correction_applied[1]",
                    item,
                ),
            )

        vectors = GeometryVectors(
            earth_to_spacecraft=position_vector(
                "Vector_Cartesian_Position_Earth_To_Spacecraft"
            ),
            spacecraft_to_target=position_vector(
                "Vector_Cartesian_Position_Spacecraft_To_Target"
            ),
            sun_to_spacecraft=position_vector(
                "Vector_Cartesian_Position_Sun_To_Spacecraft"
            ),
            sun_to_target=position_vector(
                "Vector_Cartesian_Position_Sun_To_Target"
            ),
            spacecraft_relative_to_earth=velocity_vector(
                "Vector_Cartesian_Velocity_Spacecraft_Relative_To_Earth"
            ),
            spacecraft_relative_to_sun=velocity_vector(
                "Vector_Cartesian_Velocity_Spacecraft_Relative_To_Sun"
            ),
            spacecraft_relative_to_target=velocity_vector(
                "Vector_Cartesian_Velocity_Spacecraft_Relative_To_Target"
            ),
        )
        reference_time = datetime.fromisoformat(
            text(f"{orbiter_path}/geom:geometry_reference_time_utc[1]")
            .replace("Z", "+00:00")
        )
        spice_path = (
            "geom:SPICE_Kernel_Files[1]/"
            "geom:SPICE_Kernel_Identification[1]"
        )
        return cls(
            kernel_type=text(f"{spice_path}/geom:kernel_type[1]"),
            spice_kernel_file_name=text(
                f"{spice_path}/geom:spice_kernel_file_name[1]"
            ),
            image_display=image_display,
            orbiter=GeometryOrbiter(
                reference_time_utc=reference_time,
                identification=identification,
                pixel_dimensions=pixel_dimensions,
                distances=distances,
                surface=surface,
                illumination=illumination,
                vectors=vectors,
            ),
        )

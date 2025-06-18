
import React, { useLayoutEffect, useRef } from "react";
import * as am5 from "@amcharts/amcharts5";
import * as am5map from "@amcharts/amcharts5/map";
import am5themes_Animated from "@amcharts/amcharts5/themes/Animated";
import * as am5geodata_world from "@amcharts/amcharts5-geodata/worldLow";


const WorldMap = ({ country, onCountrySelect }) => {

    // stores the am5.Root instance.
    const rootRef = useRef(null);
    // holds the chart object.
    const chartRef = useRef(null);
    // stores the polygon series.
    const polygonSeriesRef = useRef(null);
    // tracks the currently active (clicked) country.
    const currentActiveRef = useRef(null);

    useLayoutEffect(() => {

        // Initializes the chart only once
        // Loads worldLow GeoJSON
        // Adds zoom controls, hover/active styles
        // Handles clicking on countries (zoom and highlight)
        if (!rootRef.current) {

            // Create root
            const root = am5.Root.new(chartRef.current);

            // Disable the logo
            root._logo.dispose();

            root.setThemes([am5themes_Animated.new(root)]);

            rootRef.current = root;

            // Create chart
            const chart = root.container.children.push(
                am5map.MapChart.new(root, {
                    panX: "rotateX",
                    panY: "none",
                    projection: am5map.geoMercator(),
                    wheelY: "zoom",
                    pinchZoom: true,
                    layout: root.verticalLayout,
                })
            );

            // Store chart and series references
            chartRef.current = chart;
            // allows you to control the map from other components if needed
            window.amChartsMap = chart;

            // Enable zoom control
            let zoomControl = chart.set("zoomControl", am5map.ZoomControl.new(root, {}));
            zoomControl.homeButton.set("visible", true);

            // Set clicking on "water" to zoom out
            chart.chartContainer.get("background").events.on("click", function () {
                chart.goHome(1000);

                if (onCountrySelect) onCountrySelect(null);  // Notify parent of reset
            })


            // Create polygon series
            const polygonSeries = chart.series.push(
                am5map.MapPolygonSeries.new(root, {
                    geoJSON: am5geodata_world.default,
                    exclude: ["AQ"], // optional: exclude Antarctica
                })
            );

            polygonSeriesRef.current = polygonSeries;

            // Configure tooltip
            polygonSeries.set("tooltip", am5.Tooltip.new(root, {
                labelText: "{name}",
                autoTextColor: false,
            }));

            // Base styling
            polygonSeries.mapPolygons.template.setAll({
                tooltipText: "{name}",
                interactive: true,
                strokeWidth: 0.5,
                stroke: am5.color(0xffffff),
                // focusable: false,   // remove default browser outline box
            });

            // Hover state
            polygonSeries.mapPolygons.template.states.create("hover", {
                fill: am5.color(0x125FA5),
            });

            // Active (clicked) state
            polygonSeries.mapPolygons.template.states.create("active", {
                fill: am5.color(0x004466),
            });

            // let currentActive;

            polygonSeries.mapPolygons.template.events.on("click", (ev) => {
                const polygon = ev.target;
                const dataItem = polygon.dataItem;

                // Get all available properties
                const countryData = {
                    id: dataItem.get("id"),
                    name: dataItem.get("name"),
                    customData: dataItem.dataContext,
                    geometry: dataItem.get("geometry"),
                    properties: dataItem.get("properties")
                };

                // Notify parent component of selection
                if (onCountrySelect) {
                    onCountrySelect(countryData.id);
                }



                if (currentActiveRef.current && currentActiveRef.current !== polygon) {
                    currentActiveRef.current.set("active", false);
                }

                // Activate current
                polygon.set("active", true);
                currentActiveRef.current = polygon;

                // Zoom to clicked country
                const geometry = dataItem.get("geometry");
                const geoPoint = geometry ? am5map.getGeoCentroid(geometry) : null;
                if (geoPoint) {
                    chart.zoomToGeoPoint(geoPoint, 4, true, 1000); // smooth 1-second animation
                }

                // Show tooltip manually
                polygon.showTooltip();
            });
        }

        return () => {
            // Cleanup only on unmount
            if (rootRef.current && !rootRef.current.isDisposed()) {
                rootRef.current.dispose();
                rootRef.current = null;
            }
        };

    }, []);

    // Effect to handle country changes
    // On prop change, finds and zooms to the specified country
    // Applies the active color
    useLayoutEffect(() => {

        if (!country && currentActiveRef.current) {
            currentActiveRef.current.set("active", false);
            currentActiveRef.current = null;
            chartRef.current.goHome();
        }

        if (!country || !polygonSeriesRef.current) return;

        const dataItem = polygonSeriesRef.current.getDataItemById(country);
        if (!dataItem) return;

        if (currentActiveRef.current) {
            currentActiveRef.current.set("active", false);
        }

        const polygon = dataItem.get("mapPolygon");
        polygon.set("active", true);
        currentActiveRef.current = polygon;

        const geoPoint = am5map.getGeoCentroid(dataItem.get("geometry"));
        if (geoPoint && chartRef.current) {
            chartRef.current.zoomToGeoPoint(geoPoint, 4, true, 1000);
        }
    }, [country]); // Add country to dependency array

    return <div ref={chartRef} style={{ width: "100%", height: "500px" }} />;
};

export default WorldMap;

<?xml version="1.0" encoding="UTF-8"?>
<!--
  Ancient Aliens GIS — site symbology.

  OGC Styled Layer Descriptor 1.0.0 with Symbology Encoding filters. Written
  against the SLD 1.0.0 profile GeoServer accepts for WMS 1.3.0, so the WMS
  rendering matches the browser client's pin colours: both read from the same
  category vocabulary, and the hex values here are the cat-* custom properties from
  assets/css/tokens.css.

  Rules are scale-dependent: a world view draws dots, a regional view draws
  marked pins, and a local view adds a label.
-->
<StyledLayerDescriptor version="1.0.0"
    xmlns="http://www.opengis.net/sld"
    xmlns:ogc="http://www.opengis.net/ogc"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.opengis.net/sld
                        http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd">
  <NamedLayer>
    <Name>aagis:sites</Name>
    <UserStyle>
      <Name>ancient-aliens-sites</Name>
      <Title>Ancient Aliens sites — by category</Title>
      <Abstract>Dark cyberpunk symbology keyed to the site category, with
        scale-dependent detail and labels at local scales.</Abstract>
      <IsDefault>1</IsDefault>

      <FeatureTypeStyle>
        <!-- ============ world / continental: small glowing dots ========== -->
        <Rule>
          <Name>world-dots</Name>
          <Title>Sites (world view)</Title>
          <MinScaleDenominator>12000000</MinScaleDenominator>
          <PointSymbolizer>
            <Graphic>
              <Mark>
                <WellKnownName>circle</WellKnownName>
                <Fill>
                  <CssParameter name="fill">
                    <ogc:Function name="Recode">
                      <ogc:PropertyName>category</ogc:PropertyName>
                      <ogc:Literal>megalithic</ogc:Literal>  <ogc:Literal>#7dd3e8</ogc:Literal>
                      <ogc:Literal>pyramid</ogc:Literal>     <ogc:Literal>#ffb347</ogc:Literal>
                      <ogc:Literal>geoglyph</ogc:Literal>    <ogc:Literal>#8ef26b</ogc:Literal>
                      <ogc:Literal>underground</ogc:Literal> <ogc:Literal>#b98cff</ogc:Literal>
                      <ogc:Literal>underwater</ogc:Literal>  <ogc:Literal>#39c6ff</ogc:Literal>
                      <ogc:Literal>ufo</ogc:Literal>         <ogc:Literal>#ff4fd8</ogc:Literal>
                      <ogc:Literal>military</ogc:Literal>    <ogc:Literal>#ff6b5b</ogc:Literal>
                      <ogc:Literal>research</ogc:Literal>    <ogc:Literal>#4fe0d4</ogc:Literal>
                      <ogc:Literal>sacred</ogc:Literal>      <ogc:Literal>#ffd84f</ogc:Literal>
                      <ogc:Literal>anomaly</ogc:Literal>     <ogc:Literal>#ff8ae6</ogc:Literal>
                      <ogc:Literal>landform</ogc:Literal>    <ogc:Literal>#a4b8c4</ogc:Literal>
                      <ogc:Literal>city</ogc:Literal>        <ogc:Literal>#ff9b5b</ogc:Literal>
                      <ogc:Literal>artifact</ogc:Literal>    <ogc:Literal>#d9c48a</ogc:Literal>
                      <ogc:Literal>region</ogc:Literal>      <ogc:Literal>#5f7b8c</ogc:Literal>
                      <ogc:Literal>offworld</ogc:Literal>    <ogc:Literal>#c7a6ff</ogc:Literal>
                    </ogc:Function>
                  </CssParameter>
                  <CssParameter name="fill-opacity">0.95</CssParameter>
                </Fill>
                <Stroke>
                  <CssParameter name="stroke">#04070d</CssParameter>
                  <CssParameter name="stroke-width">1</CssParameter>
                </Stroke>
              </Mark>
              <Size>7</Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>

        <!-- ============ regional: ringed pin ============================= -->
        <Rule>
          <Name>regional-pins</Name>
          <Title>Sites (regional view)</Title>
          <MinScaleDenominator>250000</MinScaleDenominator>
          <MaxScaleDenominator>12000000</MaxScaleDenominator>
          <PointSymbolizer>
            <Graphic>
              <Mark>
                <WellKnownName>circle</WellKnownName>
                <Fill>
                  <CssParameter name="fill">#070b14</CssParameter>
                  <CssParameter name="fill-opacity">0.85</CssParameter>
                </Fill>
                <Stroke>
                  <CssParameter name="stroke">
                    <ogc:Function name="Recode">
                      <ogc:PropertyName>category</ogc:PropertyName>
                      <ogc:Literal>megalithic</ogc:Literal>  <ogc:Literal>#7dd3e8</ogc:Literal>
                      <ogc:Literal>pyramid</ogc:Literal>     <ogc:Literal>#ffb347</ogc:Literal>
                      <ogc:Literal>geoglyph</ogc:Literal>    <ogc:Literal>#8ef26b</ogc:Literal>
                      <ogc:Literal>underground</ogc:Literal> <ogc:Literal>#b98cff</ogc:Literal>
                      <ogc:Literal>underwater</ogc:Literal>  <ogc:Literal>#39c6ff</ogc:Literal>
                      <ogc:Literal>ufo</ogc:Literal>         <ogc:Literal>#ff4fd8</ogc:Literal>
                      <ogc:Literal>military</ogc:Literal>    <ogc:Literal>#ff6b5b</ogc:Literal>
                      <ogc:Literal>research</ogc:Literal>    <ogc:Literal>#4fe0d4</ogc:Literal>
                      <ogc:Literal>sacred</ogc:Literal>      <ogc:Literal>#ffd84f</ogc:Literal>
                      <ogc:Literal>anomaly</ogc:Literal>     <ogc:Literal>#ff8ae6</ogc:Literal>
                      <ogc:Literal>landform</ogc:Literal>    <ogc:Literal>#a4b8c4</ogc:Literal>
                      <ogc:Literal>city</ogc:Literal>        <ogc:Literal>#ff9b5b</ogc:Literal>
                      <ogc:Literal>artifact</ogc:Literal>    <ogc:Literal>#d9c48a</ogc:Literal>
                      <ogc:Literal>region</ogc:Literal>      <ogc:Literal>#5f7b8c</ogc:Literal>
                      <ogc:Literal>offworld</ogc:Literal>    <ogc:Literal>#c7a6ff</ogc:Literal>
                    </ogc:Function>
                  </CssParameter>
                  <CssParameter name="stroke-width">2.2</CssParameter>
                </Stroke>
              </Mark>
              <Size>14</Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>

        <!-- ============ local: pin + label =============================== -->
        <Rule>
          <Name>local-labelled</Name>
          <Title>Sites (local view, labelled)</Title>
          <MaxScaleDenominator>250000</MaxScaleDenominator>
          <PointSymbolizer>
            <Graphic>
              <Mark>
                <WellKnownName>circle</WellKnownName>
                <Fill>
                  <CssParameter name="fill">#070b14</CssParameter>
                </Fill>
                <Stroke>
                  <CssParameter name="stroke">#22e0f2</CssParameter>
                  <CssParameter name="stroke-width">2.6</CssParameter>
                </Stroke>
              </Mark>
              <Size>20</Size>
            </Graphic>
          </PointSymbolizer>
          <TextSymbolizer>
            <Label><ogc:PropertyName>name</ogc:PropertyName></Label>
            <Font>
              <CssParameter name="font-family">Noto Sans</CssParameter>
              <CssParameter name="font-size">13</CssParameter>
              <CssParameter name="font-weight">bold</CssParameter>
            </Font>
            <LabelPlacement>
              <PointPlacement>
                <AnchorPoint>
                  <AnchorPointX>0.5</AnchorPointX>
                  <AnchorPointY>0.0</AnchorPointY>
                </AnchorPoint>
                <Displacement>
                  <DisplacementX>0</DisplacementX>
                  <DisplacementY>16</DisplacementY>
                </Displacement>
              </PointPlacement>
            </LabelPlacement>
            <Halo>
              <Radius>2.4</Radius>
              <Fill>
                <CssParameter name="fill">#04070d</CssParameter>
                <CssParameter name="fill-opacity">0.9</CssParameter>
              </Fill>
            </Halo>
            <Fill>
              <CssParameter name="fill">#e8f4f8</CssParameter>
            </Fill>
            <VendorOption name="autoWrap">140</VendorOption>
            <VendorOption name="maxDisplacement">40</VendorOption>
            <VendorOption name="spaceAround">6</VendorOption>
          </TextSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>

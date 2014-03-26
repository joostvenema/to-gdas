<?xml version="1.0" encoding="UTF-8"?>
  <xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message" xmlns:common="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common" xmlns:footer="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message/footer" xmlns:generic="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

    <xsl:template match="/">
      <Dataset>
        <DatasetURI>http://eurostat.org/stats/<xsl:value-of select="message:GenericData/message:Header/message:DataSetID"/></DatasetURI>
        <Title><xsl:value-of select="message:GenericData/message:Header/message:DataSetID"/></Title>
        <Organization><xsl:value-of select="message:GenericData/message:Header/message:Sender/@id"/></Organization>
        <Abstract>N_A</Abstract>
        <ReferenceDate><xsl:value-of select="message:GenericData/message:Header/message:Prepared"/></ReferenceDate>
        <Version>0</Version>
        <Documentation>N_A</Documentation>
        <Columnset>
          <FrameworkKey complete="true" relationship="one">
            <Column name="GEO" type="http://www.w3.org/TR/xmlschema-2/#string" length="4" decimals="0"/>
          </FrameworkKey>
          <Attributes>
            <xsl:for-each select="//generic:Series[1]">
              <xsl:for-each select="generic:SeriesKey/generic:Value[not(@id='GEO')]">
                <Column name="{@id}" type="http://www.w3.org/TR/xmlschema-2/#string" length="255" decimals="0" purpose="Attribute">  
                <Title/>
                <Abstract/>
                <Documentation/>
                <Values>
                  <Count>
                    <UOM><ShortForm/><LongForm/></UOM>
                  </Count>
                </Values>
                <GetDataRequest/>
                </Column>
              </xsl:for-each>
            <xsl:for-each select="generic:Obs">
              <Column name="dim_{generic:ObsDimension/@value}" type="http://www.w3.org/TR/xmlschema-2/#string" length="255" decimals="0" purpose="Attribute">  
                <Title/>
                <Abstract/>
                <Documentation/>
                <Values>
                  <Count>
                    <UOM><ShortForm/><LongForm/></UOM>
                  </Count>
                </Values>
                <GetDataRequest/>
              </Column>
            </xsl:for-each>
          </xsl:for-each>
        </Attributes>
      </Columnset>
      <Rowset>
        <xsl:for-each select="message:GenericData/message:DataSet/generic:Series">
        <Row>
          <K>
            <xsl:value-of select="generic:SeriesKey/generic:Value[@id='GEO']/@value"/>
          </K>
          <xsl:for-each select="generic:SeriesKey/generic:Value[not(@id='GEO')]">
            <V>
              <xsl:value-of select="@value"/>
            </V>
          </xsl:for-each>
          <xsl:for-each select="generic:Obs">
            <V>
              <xsl:value-of select="generic:ObsValue/@value"/>
            </V>
          </xsl:for-each>
        </Row>
      </xsl:for-each>
    </Rowset>
  </Dataset>
</xsl:template>
</xsl:stylesheet>
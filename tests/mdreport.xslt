<?xml version="1.0"?>

<!--
  Make creates a report of metadata file (i.e. an EntitiesDescriptor)
  The goal is to diff two
-->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:shibmeta="urn:mace:shibboleth:metadata:1.0"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
  xmlns:xi="http://www.w3.org/2001/XInclude" xmlns:shibmd="urn:mace:shibboleth:metadata:1.0"
  xmlns:mdrpi="urn:oasis:names:tc:SAML:metadata:rpi">
  <xsl:output method="text" omit-xml-declaration="yes"/>

  <xsl:template match="@*|node()">
    <xsl:apply-templates select="@*|node()"/>
  </xsl:template>

  <!-- Ignore comments -->
  <xsl:template match="comment()"/>

  <!-- Output modified EntitiesDescriptor -->
  <xsl:template match="/md:EntitiesDescriptor">
    <xsl:text>EntitiesDescriptor: Name=</xsl:text>
    <xsl:value-of select="@Name"/>
    <xsl:text>&#xa;</xsl:text>
    <!-- List direct child elements that are not EntityDescriptor -->
    <xsl:for-each select='./*[local-name()!="EntityDescriptor"]'>
      <xsl:text> </xsl:text>
      <xsl:value-of select="name()"/>
    </xsl:for-each>
    <xsl:text>&#xa;</xsl:text>
    <xsl:for-each select="md:EntityDescriptor">
      <xsl:sort select="@entityID"/>
      <xsl:apply-templates select="."/>
    </xsl:for-each>
  </xsl:template>

  <!-- EntityDescriptor -->
  <xsl:template match="md:EntityDescriptor">
    <xsl:text>EntityDescriptor: entityID=</xsl:text>
    <xsl:value-of select="@entityID"/>
    <xsl:text>; #elements=</xsl:text>
    <!-- Count of all elements below the current node -->
    <xsl:value-of select="count(.//*)"/>
    <!-- Count of all attributes below the current node -->
    <xsl:text>; #attributes=</xsl:text>
    <xsl:value-of select="count(.//@*)"/>
    <xsl:text>&#xa;</xsl:text>
    <!-- List names of direct childs in document order -->
    <xsl:for-each select="./*">
      <xsl:text> </xsl:text>
      <xsl:value-of select="name()"/>
    </xsl:for-each>
    <xsl:text>&#xa;</xsl:text>
  </xsl:template>

</xsl:stylesheet>

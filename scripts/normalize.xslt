<?xml version="1.0"?>

<!--
  Stylesheet that Normalises an EntitiesDescriptor
  The goal is to minimise the differences between versions of the same metadata. Actions:
  * Suppresses comments
  * Outputs EntityDescriptor elements ordered by registrationAuthority and entityID
  Should be run just before signing the EntitiesDescriptor
-->

<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:shibmeta="urn:mace:shibboleth:metadata:1.0"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
                xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
		        xmlns:xi="http://www.w3.org/2001/XInclude"
                xmlns:shibmd="urn:mace:shibboleth:metadata:1.0"
                xmlns:mdrpi="urn:oasis:names:tc:SAML:metadata:rpi">
  
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>
  
  <!-- Do not copy comments -->
  <xsl:template match="comment()"/>
  
  <!-- Output modified EntitiesDescriptor -->
  <xsl:template match="/md:EntitiesDescriptor">
    <xsl:copy> <!-- Copy EntitiesDescriptor node -->
      <xsl:copy-of select="@*"/> <!-- and its attributes ... -->
      <!-- Note: for the sake of completeness the Signature elelement is copied although
           more likely thant not our modifications will break the signature-->
      <xsl:apply-templates select="md:Signature"/> 
      <xsl:apply-templates select="md:Extensions"/> <!-- copy extensions -->
      <!-- Output EntityDescriptor elements sorted by registrationAuthority (primary( and entityID (secondary) -->
      <xsl:for-each select="md:EntityDescriptor">
        <xsl:sort select="md:Extensions/mdrpi:RegistrationInfo/@registrationAuthority"/>
        <xsl:sort select="@entityID"/>
        <xsl:apply-templates select="."/>
      </xsl:for-each>      
    </xsl:copy>
  </xsl:template>
  
</xsl:stylesheet>
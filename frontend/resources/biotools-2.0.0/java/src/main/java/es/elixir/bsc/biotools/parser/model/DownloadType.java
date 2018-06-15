/**
 * *****************************************************************************
 * Copyright (C) 2016 ELIXIR ES, Spanish National Bioinformatics Institute (INB)
 * and Barcelona Supercomputing Center (BSC)
 *
 * Modifications to the initial code base are copyright of their respective
 * authors, or their employers as appropriate.
 * 
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301  USA
 *****************************************************************************
 */
package es.elixir.bsc.biotools.parser.model;

import javax.xml.bind.annotation.XmlEnum;
import javax.xml.bind.annotation.XmlEnumValue;

/**
 * Type of download that is linked to.
 * 
 * @author Dmitry Repchevsky
 */

@XmlEnum(EnumType.class)
public enum DownloadType {
    @XmlEnumValue("API specification") API_SPECIFICATION("API specification"),
    @XmlEnumValue("Biological data") BIOLOGICAL_DATA("Biological data"),
    @XmlEnumValue("Binaries") BINARIES("Binaries"),
    @XmlEnumValue("Binary package") BINARY_PACKAGE("Binary package"),
    @XmlEnumValue("Command-line specification") COMMANDLINE_SPECIFICATION("Command-line specification"),
    @XmlEnumValue("Container file") CONTAINER_FILE("Container file"),
    @XmlEnumValue("CWL file") CWL("CWL file"),
    @XmlEnumValue("Icon") ICON("Icon"),
    @XmlEnumValue("Ontology") ONTOLOGY("Ontology"),
    @XmlEnumValue("Screenshot") SCREENSHOT("Screenshot"),
    @XmlEnumValue("Source code") SOURCE_CODE("Source code"),
    @XmlEnumValue("Source package") SOURCE_PACKAGE("Source package"),
    @XmlEnumValue("Test data") TEST_DATA("Test data"),
    @XmlEnumValue("Test script") TEST_SCRIPT("Test script"),
    @XmlEnumValue("Tool wrapper (galaxy)") GALAXY_TOOL_WRAPPER("Tool wrapper (galaxy)"),
    @XmlEnumValue("Tool wrapper (taverna)") TAVERNA_TOOL_WRAPPER("Tool wrapper (taverna)"),
    @XmlEnumValue("Tool wrapper (other)") OTHER_TOOL_WRAPPER("Tool wrapper (other)"),
    @XmlEnumValue("VM image") VM_IMAGE("VM image");
    
    private final String value;
    
    private DownloadType(String value) {
        this.value = value;
    }
    
    @Override
    public String toString() {
        return value;
    }

    public static DownloadType fromValue(String value) {
        for (DownloadType type: DownloadType.values()) {
            if (type.value.equals(value)) {
                return type;
            }
        }
        throw new IllegalArgumentException(value);
    }
}

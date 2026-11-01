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
 * ELIXIR node.
 * 
 * @author Dmitry Repchevsky
 */

@XmlEnum(EnumType.class)
public enum ElixirNode {
    @XmlEnumValue("Belgium") BELGIUM("Belgium"),
    @XmlEnumValue("Czech Republic") CZHECH_REPUBLIC("Czech Republic"),
    @XmlEnumValue("Denmark") DENMARK("Denmark"),
    @XmlEnumValue("EMBL") EMBL("EMBL"),
    @XmlEnumValue("Estonia") ESTONIA("Estonia"),
    @XmlEnumValue("Finland") FINLAND("Finland"),
    @XmlEnumValue("France") FRANCE("France"),
    @XmlEnumValue("Germany") GERMANY("Germany"),
    @XmlEnumValue("Greece") GREECE("Greece"),
    @XmlEnumValue("Netherlands") NETHERLANDS("Netherlands"),
    @XmlEnumValue("Norway") NORWAY("Norway"),
    @XmlEnumValue("Ireland") IRELAND("Ireland"),
    @XmlEnumValue("Israel") ISRAEL("Israel"),
    @XmlEnumValue("Italy") ITALY("Italy"),
    @XmlEnumValue("Luxembourg") LUXEMBURG("Luxembourg"),
    @XmlEnumValue("Portugal") PORTUGAL("Portugal"),
    @XmlEnumValue("Slovenia") SLOVENIA("Slovenia"),
    @XmlEnumValue("Spain") SPAIN("Spain"),
    @XmlEnumValue("Sweden") SWEDEN("Sweden"),
    @XmlEnumValue("Switzerland") SWITZERLAND("Switzerland"),
    @XmlEnumValue("UK") UK("UK");
    
    private final String value;
    
    private ElixirNode(String value) {
        this.value = value;
    }
    
    @Override
    public String toString() {
        return value;
    }

    public static ElixirNode fromValue(String value) {
        for (ElixirNode type: ElixirNode.values()) {
            if (type.value.equals(value)) {
                return type;
            }
        }
        throw new IllegalArgumentException(value);
    }
}

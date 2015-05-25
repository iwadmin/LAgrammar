/* LanguageTool, a natural language style checker 
 * Copyright (C) 2014 Daniel Naber (http://www.danielnaber.de)
 * 
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
 * USA
 */
package org.languagetool.rules;

import org.junit.Test;
import org.languagetool.JLanguageTool;

import java.io.IOException;
import java.io.InputStream;
import java.util.Map;

import static junit.framework.TestCase.assertTrue;

public class ConfusionSetLoaderTest {
  
  @Test
  public void testWithDefaultLimits() throws IOException {
    InputStream inputStream = JLanguageTool.getDataBroker().getFromResourceDirAsStream("/yy/homophones.txt");
    ConfusionSetLoader loader = new ConfusionSetLoader();
    Map<String,ConfusionProbabilityRule.ConfusionSet> map = loader.loadConfusionSet(inputStream);
    assertTrue(map.size() == 2);
  }

  @Test
  public void testLoadWithStrictLimits() throws IOException {
    InputStream inputStream = JLanguageTool.getDataBroker().getFromResourceDirAsStream("/yy/homophones.txt");
    InputStream infoStream = JLanguageTool.getDataBroker().getFromResourceDirAsStream("/yy/homophones-info.txt");
    ConfusionSetLoader loader2 = new ConfusionSetLoader(infoStream, 1002, 10.0f);
    assertTrue(loader2.loadConfusionSet(inputStream).size() == 0);
  }
}

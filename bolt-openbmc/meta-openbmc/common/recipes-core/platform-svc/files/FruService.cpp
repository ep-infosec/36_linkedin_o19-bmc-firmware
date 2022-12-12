/*
 * FruService.cpp
 *
 * Copyright 2017-present Facebook. All Rights Reserved.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 */

#include <glog/logging.h>
#include "FruService.h"

namespace openbmc {
namespace qin {

FruService::FruService (const std::string & dbusName,
                        const std::string & dbusPath,
                        const std::string & dbusInteface) {
  this->dbusName_ = dbusName;
  this->dbusPath_ = dbusPath;
  this->dbusInteface_ = dbusInteface;
  isAvailable_ = false;
}

const std::string & FruService::getDBusName() const{
  return dbusName_;
}

const std::string & FruService::getDBusPath() const{
  return dbusPath_;
}

bool FruService::isAvailable() const {
  return isAvailable_;
}

bool FruService::setIsAvailable(bool isAvailable) {
  if (this->isAvailable_ == isAvailable) {
    //No change in availability
    return true;
  }

  if (isAvailable == true) {
    GError *error = nullptr;
    proxy_ = g_dbus_proxy_new_for_bus_sync(
                        G_BUS_TYPE_SYSTEM,
                        G_DBUS_PROXY_FLAGS_NONE,
                        nullptr,
                        dbusName_.c_str(),
                        dbusPath_.c_str(),
                        dbusInteface_.c_str(),
                        nullptr,
                        &error);

    if (error != nullptr) {
      //Error in setting up proxy_
      LOG(ERROR) << "Error in setting up proxy to "
                 << dbusName_ << " :" << error->message;
      return false;
    }
  }
  else {
    if (proxy_ != nullptr) {
      g_object_unref(proxy_);
    }
  }

  this->isAvailable_ = isAvailable;
  return true;
}

bool FruService::reset() {
  if (isAvailable_) {
    GError *error = nullptr;
    // Reset FruTree at Fru Service
    g_dbus_proxy_call_sync(
        proxy_,
        "resetTree",
        nullptr,
        G_DBUS_CALL_FLAGS_NONE,
        -1,
        nullptr,
        &error);

    if (error != nullptr) {
      LOG(ERROR) << "Error in reset " << dbusName_ << " :" << error->message;
    }
    else {
      return true;
    }
  }

  return false;
}

bool FruService::addFRU(const std::string & fruParentPath,
                        const std::string & fruJson) {
  LOG(INFO) << "addFRU " << fruParentPath << " " << fruJson;

  if (isAvailable_) {
    GError* error = nullptr;
    GVariant* response;
    gboolean status;

    std::string path = dbusPath_ + fruParentPath;

    response = g_dbus_proxy_call_sync(
                        proxy_,
                        "addFRU",
                        g_variant_new("(ss)", path.c_str(), fruJson.c_str()),
                        G_DBUS_CALL_FLAGS_NONE,
                        -1,
                        nullptr,
                        &error);

    if (error != nullptr) {
      LOG(ERROR) << "Error in addFRU " << dbusName_ << " :" << error->message;
    }
    else {
      g_variant_get(response, "(b)", &status);
      if (status == TRUE) {
        return true;
      }
    }
  }

  return false;
}

bool FruService::removeFRU(std::string fruPath) {
  LOG(INFO) << "removeFRU " << fruPath;

  if (isAvailable_) {
    GError* error = nullptr;
    GVariant* response;
    gboolean status;

    fruPath = dbusPath_ + fruPath;

    g_dbus_proxy_call_sync(
        proxy_,
        "removeFRU",
        g_variant_new("(&s)", fruPath.c_str()),
        G_DBUS_CALL_FLAGS_NONE,
        -1,
        nullptr,
        &error);

    if (error != nullptr) {
      LOG(ERROR) << "Error in removeFRU "
                 << dbusName_ << " :" << error->message;
    }
    else {
      g_variant_get(response, "(b)", &status);
      if (status == TRUE) {
        return true;
      }
    }
  }

  return false;
}

} // namespace qin
} // namespace openbmc

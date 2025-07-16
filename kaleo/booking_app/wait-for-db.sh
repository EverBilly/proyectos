#!/bin/sh
until mysqladmin ping -h db -u booking_user -pbooking_pass --silent; do
  sleep 1
done
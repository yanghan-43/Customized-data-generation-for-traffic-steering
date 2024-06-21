from config import *
from personal_equipment import PersonalEquipment
from category import Category
import csv_record
from cell import Cell
from utils import *
from cell_barring import *
import pandas as pd
import pprint
import time, os
import datetime

import matplotlib
matplotlib.use('TkAgg')

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
import matplotlib.pyplot as plt

def simulation(cells, folder_path, cells_x_coordinates, cells_y_coordinates, pes_x_coordinates, pes_y_coordinates):
    multiplier = 1

    for t in range(SIM_TIME):
        # Determine handover rates
        handover_rate = {}

        for cell in cells:

            ho_rate_cat = {}
            for cat in cell.cat_list:

                ho_rate_pe = {}
                # In this loop, based on the SIM_TIME length, set the handover modes based on the time of the day.
                # In original scenario, One day consists of 96 ticks. (each 15 minutes is 1 sim time iteration)
                for pe in cat.pe_list:
                    if t % 96 >= 0 and t % 96 < 24:
                        pe.set_handover_mode(0, cell.radius)
                    elif t % 96 >= 24 and t % 96 < 28:
                        pe.set_handover_mode(4, cell.radius)
                    elif t % 96 >= 28 and t % 96 < 38:
                        pe.set_handover_mode(1, cell.radius)
                    elif t % 96 >= 38 and t % 96 < 44:
                        pe.set_handover_mode(2, cell.radius)
                    elif t % 96 >= 44 and t % 96 < 52:
                        pe.set_handover_mode(3, cell.radius)
                    elif t % 96 >= 52 and t % 96 < 64:
                        pe.set_handover_mode(2, cell.radius)
                    elif t % 96 >= 64 and t % 96 < 80:
                        pe.set_handover_mode(1, cell.radius)
                    elif t % 96 >= 80 and t % 96 < 88:
                        pe.set_handover_mode(4, cell.radius)
                    elif t % 96 >= 88 and t % 96 < 96:
                        pe.set_handover_mode(0, cell.radius)

                    ho_rate_pe[pe.pe_id] = pe.get_normal_distribution()

                ho_rate_cat[cat.cat_id] = ho_rate_pe  # pe handover dic

            handover_rate[cell.id] = ho_rate_cat  # cell handover dic

        # now we need to assign handovers to other cells and categories.
        for cell_i_id, cell_j_id_list in OUTFLOW_SETTING.items():
            # first remove the load from cell_i

            for cat in cells[cell_i_id].cat_list:
                for pe in cat.pe_list:
                    pre_load = pe.load  # initial load
                    new_load = pre_load - handover_rate[cell_i_id][cat.cat_id][pe.pe_id]
                    pe.set_load(new_load)
            # now add necessary load to others
            load_divider = len(cell_j_id_list)
            for cell_j_id in cell_j_id_list:
                for cat in cells[cell_j_id].cat_list:
                    for pe in cat.pe_list:
                        pre_load = pe.load
                        new_load = pre_load + (handover_rate[cell_i_id][cat.cat_id][pe.pe_id] / load_divider)
                        pe.set_load(new_load)

        # now loads are balanced, write information to dictionary so that we can convert it to pandas and csv

        for cell in cells:
            pe_load_sum = 0

            for cat in cell.cat_list:
                for pe in cat.pe_list:
                    if cell.id == 0:
                        csv_record.cell_0_results.append([t, cat.cat_id, pe.pe_id, pe.load * multiplier])
                        pe_load_sum = pe_load_sum + pe.load
                    if cell.id == 1:
                        csv_record.cell_1_results.append([t, cat.cat_id, pe.pe_id, pe.load * multiplier])
                        pe_load_sum = pe_load_sum + pe.load
                    if cell.id == 2:
                        csv_record.cell_2_results.append([t, cat.cat_id, pe.pe_id, pe.load * multiplier])
                        pe_load_sum = pe_load_sum + pe.load
                    if cell.id == 3:
                        csv_record.cell_3_results.append([t, cat.cat_id, pe.pe_id, pe.load * multiplier])
                        pe_load_sum = pe_load_sum + pe.load
                    if cell.id == 4:
                        csv_record.cell_4_results.append([t, cat.cat_id, pe.pe_id, pe.load * multiplier])
                        pe_load_sum = pe_load_sum + pe.load
                    if cell.id == 5:
                        csv_record.cell_5_results.append([t, cat.cat_id, pe.pe_id, pe.load * multiplier])
                        pe_load_sum = pe_load_sum + pe.load
                    if cell.id == 6:
                        csv_record.cell_6_results.append([t, cat.cat_id, pe.pe_id, pe.load * multiplier])
                        pe_load_sum = pe_load_sum + pe.load

            cell.load = pe_load_sum

            if pe_load_sum >= 45:
                cell.cell_barring_flag = 1
                if cell.radius >= 60:
                    cell.radius = cell.radius - 20
            else:
                cell.cell_barring_flag = 0

            if cell.id == 0:
                csv_record.cell_0_total_load_results.append([t, pe_load_sum, cell.cell_barring_flag, cell.radius])
            if cell.id == 1:
                csv_record.cell_1_total_load_results.append([t, pe_load_sum, cell.cell_barring_flag, cell.radius])
            if cell.id == 2:
                csv_record.cell_2_total_load_results.append([t, pe_load_sum, cell.cell_barring_flag, cell.radius])
            if cell.id == 3:
                csv_record.cell_3_total_load_results.append([t, pe_load_sum, cell.cell_barring_flag, cell.radius])
            if cell.id == 4:
                csv_record.cell_4_total_load_results.append([t, pe_load_sum, cell.cell_barring_flag, cell.radius])
            if cell.id == 5:
                csv_record.cell_5_total_load_results.append([t, pe_load_sum, cell.cell_barring_flag, cell.radius])
            if cell.id == 6:
                csv_record.cell_6_total_load_results.append([t, pe_load_sum, cell.cell_barring_flag, cell.radius])

        csv_record.save_result_csv(folder_path)
        cells_figure(cells, cells_x_coordinates, cells_y_coordinates, pes_x_coordinates, pes_y_coordinates, "before barring")

        if CELL_BARRING:
            pes_x_coordinates, pes_y_coordinates = \
                cell_barring(cells, cells_x_coordinates, cells_y_coordinates, pes_x_coordinates, pes_y_coordinates)
        cells_figure(cells, cells_x_coordinates, cells_y_coordinates, pes_x_coordinates, pes_y_coordinates, "after_barring")

    return


def cells_figure(cells, cells_x_coordinates, cells_y_coordinates, pes_x_coordinates, pes_y_coordinates, barring_stap):

    path = f'D:\\{barring_stap}'
    fig_path = f'{path}+saved_samples.pdf'
    plt.subplots(figsize=(20, 20))
    for cell in cells:
        circle = plt.Circle((cells_x_coordinates[cell.id], cells_y_coordinates[cell.id]), cell.radius/30, fill=False,
                            linewidth=4)
        plt.gca().add_artist(circle)
        plt.scatter(pes_x_coordinates[cell.id], pes_y_coordinates[cell.id], linewidth=4)

    plt.xlim(-10, 10)
    plt.ylim(-10, 10)
    plt.xticks(size=25)
    plt.yticks(size=25)
    plt.grid(alpha=0.9)
    # plt.savefig('D:\\saved_samples.pdf')
    plt.savefig(fig_path)
    plt.show()
    # plt.pause(20)
    # plt.close()
    return


# returns cell list
def create_scenerio(inflow_setting, outflow_setting):
    scenerio = []

    for x in range(CELL_NUMBER):

        cat_list = []

        for y in range(CAT_NUMBER):

            pe_load_dict = INITIAL_CONFIG[y]  # percentages of pe types under category y
            pe_list = []

            for z in range(PE_NUMBER):  # 0: "iot", 1: "vehicle", 2: "cell_phone", 3: "smart_watch", 4: "tablet"
                pe = PersonalEquipment(z, pe_load_dict[z])  # num of pe types one PRB for one type
                pe.assign_category(y)
                pe_list.append(pe)

            cat = Category(y, pe_list)
            cat_list.append(cat)

        cell = Cell(x, cat_list)
        cell.assign_flow_lists(inflow_setting[x], outflow_setting[y])
        cell.assign_handover_setting(HANDOVER_SETTING[x])
        scenerio.append(cell)

    cells_x_coordinates, cells_y_coordinates, pes_x_coordinates, pes_y_coordinates = cells_fig(scenerio, CELL_RADIUS)
    return scenerio, cells_x_coordinates, cells_y_coordinates, pes_x_coordinates, pes_y_coordinates


def cells_fig(cells, cell_radius):
    plt_radius = cell_radius / 30
    cells_x_coordinates = {}
    cells_y_coordinates = {}
    pes_x_coordinates = {}
    pes_y_coordinates = {}

    for cell in cells:
        if cell.id == 0:
            x_0 = 0
            y_0 = 0
            cells_x_coordinates.update({cell.id: x_0})
            cells_y_coordinates.update({cell.id: y_0})
        if cell.id == 1:
            x1, y1 = -3, 4
            cells_x_coordinates.update({cell.id: x1})
            cells_y_coordinates.update({cell.id: y1})
        if cell.id == 2:
            x2, y2 = -5, 0
            cells_x_coordinates.update({cell.id: x2})
            cells_y_coordinates.update({cell.id: y2})
        if cell.id == 3:
            x3, y3 = -3, -4
            cells_x_coordinates.update({cell.id: x3})
            cells_y_coordinates.update({cell.id: y3})
        if cell.id == 4:
            x4, y4 = 3, -4
            cells_x_coordinates.update({cell.id: x4})
            cells_y_coordinates.update({cell.id: y4})
        if cell.id == 5:
            x5, y5 = 5, 0
            cells_x_coordinates.update({cell.id: x5})
            cells_y_coordinates.update({cell.id: y5})
        if cell.id == 6:
            x6, y6 = 3, 4
            cells_x_coordinates.update({cell.id: x6})
            cells_y_coordinates.update({cell.id: y6})

    for cell in cells:
        pe_number = NUMBER_PE
        ax_x = []
        ax_y = []

        for i in range(pe_number):
            i = random.uniform(cells_x_coordinates[cell.id] - 2, cells_x_coordinates[cell.id] + 2)
            ax_x.append(i)
        pes_x_coordinates.update({cell.id: ax_x})

        for j in range(pe_number):
            j = random.uniform(cells_y_coordinates[cell.id] - 2, cells_y_coordinates[cell.id] + 2)
            ax_y.append(j)
        pes_y_coordinates.update({cell.id: ax_y})

    plt.subplots(figsize=(20, 20))
    for cell in cells:
        circle = plt.Circle((cells_x_coordinates[cell.id], cells_y_coordinates[cell.id]), plt_radius, fill=False,
                            linewidth=4)
        plt.gca().add_artist(circle)
        plt.scatter(pes_x_coordinates[cell.id], pes_y_coordinates[cell.id], linewidth=4)

    plt.xlim(-10, 10)
    plt.ylim(-10, 10)
    plt.xticks(size=25)
    plt.yticks(size=25)
    plt.grid(alpha=0.9)
    #plt.savefig('D:\\saved_samples.pdf')
    plt.show()
    #plt.pause(20)
    #plt.close()
    return cells_x_coordinates, cells_y_coordinates, pes_x_coordinates, pes_y_coordinates


def create_inflow_setting(outflow):
    # input type : {cell_id : [list of other cell ids]}
    # output type : {cell_id : [{cell_id: ratio }]}
    cell_ratios = {key: 1 / len(value) for key, value in outflow.items()}
    return {key: [{v: cell_ratios[v]} for v in value] for key, value in outflow.items()}


def _print_scenario(cells):
    for cell in cells:
        print(f"Cell id: {cell.id} : ")
        for cat in cell.cat_list:
            print(f"Cat id: {cat.cat_id} : ")
            for pe in cat.pe_list:
                print(
                    f"PE Name: {pe.pe_name} Load: {pe.init_load} Ho_param: {pe.handover_param} Ho_mean: {pe.handover_mean} Ho_var: {pe.handover_var}")

        print()


if __name__ == '__main__':
    start_time = time.time()

    inflow_setting = create_inflow_setting(OUTFLOW_SETTING)

    current_time = datetime.datetime.now().strftime('%b.%d_%H.%M.%S')
    folder_path = f'saved_results/{current_time}'
    try:
        os.makedirs(folder_path)
    except FileExistsError:
        print("Folder already exists")


    print("Scenario will be created")

    cells, cells_x_coordinates, cells_y_coordinates, pes_x_coordinates, pes_y_coordinates = create_scenerio(inflow_setting, OUTFLOW_SETTING)

    print("Scenario created, simulation will start")

    # time iteration and creating the data frame
    simulation(cells, folder_path, cells_x_coordinates, cells_y_coordinates, pes_x_coordinates, pes_y_coordinates)

    print("Simulation ended, data will be exported")

    print("Data export completed")
    print("--- %s seconds ---" % (time.time() - start_time))
